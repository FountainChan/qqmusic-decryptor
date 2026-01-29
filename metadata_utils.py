#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FLAC 元数据处理工具模块
用于为 FLAC 文件添加音轨号等元数据
"""

import re
import os
import logging
from mutagen.flac import FLAC, FLACNoHeaderError, Picture
from qqmusic_api_client import QQMusicAPIClient, get_album_metadata_cached

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_track_number_from_filename(filename):
    """
    从文件名中提取音轨号

    支持的文件名格式：
    - "01 歌曲名.flac"
    - "1-歌曲名.flac"
    - "12. 另一首歌.flac"
    - "歌曲名.flac" (返回 None)

    Args:
        filename (str): 文件名（不含路径）

    Returns:
        int or None: 提取到的音轨号，如果未找到则返回 None
    """
    # 移除扩展名
    basename = os.path.splitext(filename)[0]

    # 尝试匹配开头的数字
    # 模式1: 数字+空格 (如 "01 歌曲名")
    match = re.match(r'^(\d+)\s', basename)
    if match:
        return int(match.group(1))

    # 模式2: 数字+分隔符 (如 "1-歌曲名", "12.歌曲名")
    match = re.match(r'^(\d+)[\-\.\s]', basename)
    if match:
        return int(match.group(1))

    # 模式3: 纯数字前缀 (如 "12歌曲名")
    match = re.match(r'^(\d+)', basename)
    if match:
        # 确保数字后面还有内容（不是整个文件名都是数字）
        if len(match.group(1)) < len(basename):
            return int(match.group(1))

    # 未找到音轨号
    return None


def add_track_number_to_flac(flac_file_path, track_number, total_tracks=None):
    """
    为 FLAC 文件添加音轨号元数据

    Args:
        flac_file_path (str): FLAC 文件路径
        track_number (int): 音轨号
        total_tracks (int, optional): 专辑总音轨数

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(flac_file_path):
            logger.error(f"文件不存在: {flac_file_path}")
            return False

        # 检查是否是支持的文件格式（FLAC 或 OGG）
        if not flac_file_path.lower().endswith(('.flac', '.ogg')):
            logger.error(f"不是支持的文件格式（.flac/.ogg）: {flac_file_path}")
            return False

        # 加载FLAC文件
        audio = FLAC(flac_file_path)

        # 设置音轨号（转换为字符串）
        audio["TRACKNUMBER"] = str(track_number)

        # 如果提供了总音轨数，也设置
        if total_tracks is not None:
            audio["TRACKTOTAL"] = str(total_tracks)

        # 保存元数据
        audio.save()

        logger.info(f"成功添加音轨号: {track_number} 到 {os.path.basename(flac_file_path)}")
        return True

    except FLACNoHeaderError:
        logger.error(f"不是有效的FLAC文件: {flac_file_path}")
        return False
    except Exception as e:
        logger.error(f"添加音轨号失败 {os.path.basename(flac_file_path)}: {e}")
        return False


def process_flac_file_metadata(flac_file_path, total_tracks=None, verbose=False):
    """
    处理单个 FLAC 文件的元数据（从文件名提取并添加音轨号）

    Args:
        flac_file_path (str): FLAC 文件路径
        total_tracks (int, optional): 专辑总音轨数
        verbose (bool): 是否输出详细日志

    Returns:
        dict: 处理结果 {'success': bool, 'track_number': int or None, 'message': str}
    """
    result = {
        'success': False,
        'track_number': None,
        'message': ''
    }

    try:
        # 提取音轨号
        filename = os.path.basename(flac_file_path)
        track_number = extract_track_number_from_filename(filename)

        if track_number is None:
            result['message'] = f"未从文件名提取到音轨号: {filename}"
            if verbose:
                logger.info(result['message'])
            return result

        # 添加音轨号
        success = add_track_number_to_flac(flac_file_path, track_number, total_tracks)

        if success:
            result['success'] = True
            result['track_number'] = track_number
            result['message'] = f"成功添加音轨号 {track_number}"
            if verbose:
                logger.info(result['message'])
        else:
            result['message'] = f"添加音轨号失败: {filename}"

        return result

    except Exception as e:
        result['message'] = f"处理异常 {filename}: {e}"
        logger.error(result['message'])
        return result


def process_directory_flac_metadata(directory_path, total_tracks=None, verbose=False):
    """
    批量处理目录中所有 FLAC 文件的元数据
    
    Args:
        directory_path (str): 目录路径
        total_tracks (int, optional): 专辑总音轨数
        verbose (bool): 是否输出详细日志
    
    Returns:
        dict: 统计信息 {'total': int, 'success': int, 'failed': int, 'skipped': int}
    """
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    try:
        # 遍历目录
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.flac'):
                    stats['total'] += 1
                    flac_file_path = os.path.join(root, file)
                    
                    result = process_flac_file_metadata(
                        flac_file_path,
                        total_tracks,
                        verbose
                    )
                    
                    if result['success']:
                        stats['success'] += 1
                    elif result['track_number'] is None:
                        stats['skipped'] += 1
                    else:
                        stats['failed'] += 1
        
        return stats
    
    except Exception as e:
        logger.error(f"批量处理异常: {e}")
        return stats


def embed_cover_to_flac(flac_file_path, cover_data, metadata=None):
    """
    将封面嵌入到 FLAC 文件
    
    Args:
        flac_file_path (str): FLAC 文件路径
        cover_data (bytes): 封面图片数据
        metadata (dict, optional): 其他元数据
    
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 加载FLAC文件
        audio = FLAC(flac_file_path)
        
        # 清除现有封面
        audio.clear_pictures()
        
        # 创建新的封面
        image = Picture()
        image.type = 3  # 3 表示封面
        image.mime = "image/jpeg"
        image.data = cover_data
        
        # 添加封面
        audio.add_picture(image)
        
        # 添加其他元数据
        if metadata:
            for key, value in metadata.items():
                audio[key] = value
        
        # 保存
        audio.save()
        
        logger.info(f"成功嵌入封面到: {os.path.basename(flac_file_path)}")
        return True
    
    except Exception as e:
        logger.error(f"嵌入封面失败 {os.path.basename(flac_file_path)}: {e}")
        return False


def get_flac_metadata_tags(flac_file_path):
    """
    获取 FLAC 文件的元数据标签
    
    Args:
        flac_file_path (str): FLAC 文件路径
    
    Returns:
        dict: 包含 artist, album, title 的字典
    """
    try:
        audio = FLAC(flac_file_path)
        
        artist = audio.get("ARTIST", [None])[0]
        album = audio.get("ALBUM", [None])[0]
        title = audio.get("TITLE", [None])[0]
        
        return {
            "artist": artist,
            "album": album,
            "title": title
        }
    
    except Exception as e:
        logger.error(f"获取元数据失败 {flac_file_path}: {e}")
        return {
            "artist": None,
            "album": None,
            "title": None
        }


def save_cover_to_directory(album_dir, cover_data):
    """
    保存封面图片到专辑目录
    
    Args:
        album_dir (str): 专辑目录路径
        cover_data (bytes): 封面图片数据
    
    Returns:
        str: 保存的文件路径，失败返回 None
    """
    try:
        # 确保目录存在
        os.makedirs(album_dir, exist_ok=True)
        
        # 封面文件路径
        cover_path = os.path.join(album_dir, "cover.jpg")
        
        # 检查文件是否已存在
        if os.path.exists(cover_path):
            logger.info(f"封面已存在: {cover_path}")
            return cover_path
        
        # 保存封面
        with open(cover_path, 'wb') as f:
            f.write(cover_data)
        
        logger.info(f"封面已保存: {cover_path}")
        return cover_path
    
    except Exception as e:
        logger.error(f"保存封面失败 {album_dir}: {e}")
        return None


def process_album_metadata(flac_file_path, api_client=None, use_cache=True):
    """
    处理 FLAC 文件的专辑元数据（封面、发行年份）
    
    Args:
        flac_file_path (str): FLAC 文件路径
        api_client (QQMusicAPIClient, optional): API 客户端实例
        use_cache (bool): 是否使用缓存
    
    Returns:
        dict: 处理结果 {'success': bool, 'message': str, 'metadata': dict or None}
    """
    result = {
        'success': False,
        'message': '',
        'metadata': None
    }
    
    try:
        # 获取FLAC文件的元数据
        flac_tags = get_flac_metadata_tags(flac_file_path)
        artist = flac_tags.get("artist")
        album = flac_tags.get("album")
        
        # 检查必要的标签
        if not artist or not album:
            result['message'] = f"缺少必要的标签 (ARTIST 或 ALBUM): {os.path.basename(flac_file_path)}"
            logger.info(result['message'])
            return result
        
        # 创建API客户端
        if api_client is None:
            api_client = QQMusicAPIClient()
        
        # 获取专辑信息（带缓存）
        album_metadata = get_album_metadata_cached(api_client, artist, album)
        
        if not album_metadata:
            result['message'] = f"未找到专辑信息: {artist} - {album}"
            logger.warning(result['message'])
            return result
        
        # 提取信息
        cover_data = album_metadata.get("cover_data")
        pub_year = album_metadata.get("pub_year")
        pub_date = album_metadata.get("pub_date")
        genre = album_metadata.get("genre")
        
        # 构建元数据字典
        metadata_to_add = {}
        
        if pub_year:
            metadata_to_add["DATE"] = pub_year
            logger.info(f"发行年份: {pub_year}")
        
        if genre:
            metadata_to_add["GENRE"] = genre
        
        # 保存封面到专辑目录
        album_dir = os.path.dirname(flac_file_path)
        if cover_data:
            save_cover_to_directory(album_dir, cover_data)
        
        # 嵌入封面和元数据到FLAC文件
        if cover_data:
            success = embed_cover_to_flac(flac_file_path, cover_data, metadata_to_add)
        else:
            # 只有元数据（发行年份）
            success = add_track_number_to_flac(flac_file_path, 999)
            # 清除音轨号，只添加日期等元数据
            audio = FLAC(flac_file_path)
            for key, value in metadata_to_add.items():
                audio[key] = value
            audio.save()
            success = True
        
        if success:
            result['success'] = True
            result['message'] = f"成功处理专辑元数据"
            result['metadata'] = album_metadata
        else:
            result['message'] = f"处理专辑元数据失败"
        
        return result
    
    except Exception as e:
        result['message'] = f"处理专辑元数据异常 {os.path.basename(flac_file_path)}: {e}"
        logger.error(result['message'])
        return result


# 命令行使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='FLAC 元数据处理工具')
    parser.add_argument('path', help='FLAC 文件或目录路径')
    parser.add_argument('--total', type=int, help='专辑总音轨数')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    if os.path.isfile(args.path):
        # 处理单个文件
        result = process_flac_file_metadata(args.path, args.total, args.verbose)
        print(f"处理结果: {result}")
    elif os.path.isdir(args.path):
        # 处理目录
        stats = process_directory_flac_metadata(args.path, args.total, args.verbose)
        print(f"统计: 总计 {stats['total']}, 成功 {stats['success']}, "
              f"失败 {stats['failed']}, 跳过 {stats['skipped']}")
    else:
        print(f"错误: 路径不存在: {args.path}")
