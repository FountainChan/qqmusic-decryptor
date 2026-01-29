#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专辑元数据补充脚本
用于为已解密的 FLAC 文件补充封面和发行年份
"""

import os
import sys
import requests
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from metadata_utils import extract_track_number_from_filename
from pathlib import Path
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# API 配置
API_BASE_URL = "http://192.168.110.194:3200"
API_TIMEOUT = 10
REQUEST_TIMEOUT = 30


class AlbumMetadataCache:
    """专辑元数据缓存"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, data):
        self.cache[key] = data
    
    def clear(self):
        self.cache.clear()
    
    @staticmethod
    def generate_key(artist, album):
        return f"{artist}::{album}"


def extract_flac_tags(flac_file_path):
    """
    从 FLAC 文件提取标签
    
    Args:
        flac_file_path: FLAC 文件路径
    
    Returns:
        dict: {'artist': str, 'album': str, 'title': str}
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
        logger.error(f"读取标签失败 {flac_file_path}: {e}")
        return {"artist": None, "album": None, "title": None}


def extract_audio_tags(audio_file_path):
    """
    从音频文件提取标签（支持 FLAC 和 OGG）
    
    Args:
        audio_file_path: 音频文件路径（.flac 或 .ogg）
    
    Returns:
        dict: {'artist': str, 'album': str, 'title': str}
    """
    try:
        filename = audio_file_path.lower()
        
        # 根据文件类型选择提取方式
        if filename.endswith('.flac'):
            # FLAC 文件：使用 FLAC 类
            from mutagen.flac import FLAC as MutagenFLAC
            audio = MutagenFLAC(audio_file_path)
            artist = audio.get("ARTIST", [None])[0]
            album = audio.get("ALBUM", [None])[0]
            title = audio.get("TITLE", [None])[0]
            
        elif filename.endswith('.ogg'):
            # OGG 文件：使用 OggVorbis 类
            audio = OggVorbis(audio_file_path)
            
            # OGG 标签访问方式与 FLAC 不同
            artist = audio.get("ARTIST") or audio.get("ARTIST", [''])[0] or ''
            artist = str(artist) if artist else ""
            
            album = audio.get("ALBUM")
            album = str(album) if album else ""
            
            title = audio.get("TITLE")
            title = str(title) if title else ""
            
        else:
            # 不支持的格式
            logger.error(f"不支持的文件格式: {audio_file_path}")
            return {"artist": None, "album": None, "title": None}
        
        return {
            "artist": artist if artist else "",
            "album": album if album else "",
            "title": title if title else ""
        }
        
    except Exception as e:
        logger.error(f"读取标签失败 {audio_file_path}: {e}")
        return {"artist": "", "album": "", "title": ""}



def search_album(artist, album):
    """
    搜索专辑获取 albummid
    
    Args:
        artist: 歌手名
        album: 专辑名
    
    Returns:
        dict: {'albummid': str, 'singername': str, 'albumname': str}
    """
    try:
        search_key = f"{artist} {album}".strip()
        
        response = requests.get(
            f"{API_BASE_URL}/getSearchByKey",
            params={
                "key": search_key,
                "remoteplace": "album",
                "page": 1,
                "limit": 10
            },
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.error(f"搜索失败：无返回数据")
            return None
        
        songs = data["response"]["data"]["song"]["list"]
        if not songs:
            logger.warning(f"未找到专辑：{search_key}")
            return None
        
        return {
            "albummid": songs[0].get("albummid"),
            "singername": songs[0].get("singername"),
            "albumname": songs[0].get("albumname")
        }
    
    except Exception as e:
        logger.error(f"搜索专辑异常: {e}")
        return None


def get_album_info_with_date(albummid):
    """
    获取专辑信息（包含 aDate 字段）
    
    Args:
        albummid: 专辑 ID
    
    Returns:
        dict: 包含 aDate 等信息的字典
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/getAlbumInfo",
            params={"albummid": albummid},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.error(f"获取专辑信息失败：{albummid}")
            return None
        
        album_list = data["response"]["data"]["list"]
        if not album_list:
            logger.error(f"专辑列表为空：{albummid}")
            return None
        
        album_info = album_list[0]
        
        # 直接从 data 层级获取 aDate 字段
        response_data = data["response"]["data"]
        a_date = response_data.get("aDate")
        
        # 处理日期
        pub_year = ""
        pub_date = ""
        
        if a_date:
            a_date_str = str(a_date)
            pub_year = a_date_str[:4] if len(a_date_str) >= 4 else ""
            pub_date = a_date_str
            logger.info(f"找到 aDate: {a_date}")
        else:
            logger.warning("未找到 aDate 字段")
        
        return {
            "albumname": album_info.get("albumname"),
            "singername": album_info.get("singername"),
            "aDate": a_date,
            "pub_year": pub_year,
            "pub_date": pub_date,
            "genre": album_info.get("genre"),
            "language": album_info.get("language"),
            "desc": album_info.get("desc")
        }
    
    except Exception as e:
        logger.error(f"获取专辑信息异常 {albummid}: {e}")
        return None


def download_cover(albummid, size="500x500"):
    """
    下载专辑封面数据
    
    Args:
        albummid: 专辑 ID
        size: 图片尺寸
    
    Returns:
        bytes: 封面图片数据，失败返回 None
    """
    try:
        # 方式1：使用 API
        response = requests.get(
            f"{API_BASE_URL}/getImageUrl",
            params={"id": albummid, "size": size},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "response" in data and "data" in data["response"]:
            image_url = data["response"]["data"]["imageUrl"]
        else:
            image_url = None
        
        # 方式2：使用直接 URL
        if not image_url:
            image_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
            logger.warning(f"API 获取封面失败，使用直接 URL")
        
        logger.info(f"下载封面: {image_url}")
        
        # 下载图片
        response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        cover_data = response.content
        logger.info(f"封面数据大小: {len(cover_data)} bytes")
        return cover_data
    
    except Exception as e:
        logger.error(f"下载封面失败 {albummid}: {e}")
        return None


def embed_metadata_to_audio(audio_file_path, pub_year, cover_data, track_number=None):
    """
    将元数据嵌入音频文件（支持 FLAC 和 OGG）
    
    Args:
        audio_file_path: 音频文件路径（.flac 或 .ogg）
        pub_year: 发行年份（字符串，如 "2009"）
        cover_data: 封面数据
        track_number: 音轨号（整数，如 1, 2, 3...）
    
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        filename = audio_file_path.lower()
        
        if filename.endswith('.flac'):
            # FLAC 文件处理
            audio = FLAC(audio_file_path)
            
            # 清除现有封面
            audio.clear_pictures()
            
            # 添加年份（DATE 标签）
            if pub_year:
                audio["DATE"] = pub_year
                logger.info(f"添加年份 (FLAC): {pub_year}")
            
            # 添加音轨号（TRACKNUMBER 标签）
            if track_number is not None:
                # 检查是否已经有音轨号
                existing_track = audio.get("TRACKNUMBER")
                if existing_track:
                    logger.info(f"FLAC 文件已经有音轨号: {existing_track}，跳过写入")
                else:
                    # FLAC 标准使用 TRACKNUMBER 字符串
                    audio["TRACKNUMBER"] = str(track_number)
                    logger.info(f"添加音轨号 (FLAC): {track_number}")
            else:
                logger.warning(f"未找到音轨号，跳过音轨号写入")
            
            # 添加封面（PICTURE 标签）
            if cover_data:
                image = Picture()
                image.type = 3
                image.mime = "image/jpeg"
                image.data = cover_data
                
                audio.add_picture(image)
                logger.info(f"嵌入封面 (FLAC)")
            
            # 保存
            audio.save()
            logger.info(f"保存元数据 (FLAC): {os.path.basename(audio_file_path)}")
            return True
            
        elif filename.endswith('.ogg'):
            # OGG 文件处理（仅文本元数据）
            from mutagen.oggvorbis import OggVorbis
            audio = OggVorbis(audio_file_path)
            
            # 添加年份（DATE 标签）
            if pub_year:
                # OGG Vorbis 标准使用 DATE 字符串
                audio["DATE"] = pub_year
                logger.info(f"添加年份 (OGG): {pub_year}")
            
            # 添加音轨号（TRACKNUMBER 标签）
            if track_number is not None:
                # 检查是否已经有音轨号
                existing_track = audio.get("TRACKNUMBER")
                if existing_track:
                    logger.info(f"OGG 文件已经有音轨号: {existing_track}，跳过写入")
                else:
                    # OGG Vorbis 标准使用 TRACKNUMBER 字符串
                    audio["TRACKNUMBER"] = str(track_number)
                    logger.info(f"添加音轨号 (OGG): {track_number}")
            else:
                logger.warning(f"未找到音轨号，跳过音轨号写入")
            
            # 封面处理：跳过内嵌，只保存为独立文件
            # OGG Vorbis 的封面嵌入非常复杂（需要手动构建 METADATA_BLOCK_PICTURE）
            # 为了稳定性和兼容性，我们跳过内嵌，cover.jpg 会在主函数中单独保存
            if cover_data:
                logger.info(f"OGG 封面只保存为独立文件，不内嵌")
            else:
                logger.info(f"没有封面数据")
            
            # 保存
            audio.save()
            logger.info(f"保存元数据 (OGG): {os.path.basename(audio_file_path)}")
            return True
            
        else:
            # 不支持的格式
            logger.error(f"不支持的文件格式: {audio_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"嵌入元数据失败 {audio_file_path}: {e}")
        return False


def save_cover_to_directory(album_dir, cover_data):
    """
    保存封面到专辑目录
    
    Args:
        album_dir: 专辑目录路径
        cover_data: 封面数据
    
    Returns:
        str: 封面文件路径
    """
    try:
        os.makedirs(album_dir, exist_ok=True)
        
        cover_path = os.path.join(album_dir, "cover.jpg")
        
        with open(cover_path, 'wb') as f:
            f.write(cover_data)
        
        logger.info(f"保存封面: {cover_path}")
        return cover_path
    
    except Exception as e:
        logger.error(f"保存封面失败 {album_dir}: {e}")
        return None


def process_album_directory(album_dir, api_cache=None, options=None):
    """
    处理整个专辑目录（所有 FLAC 文件）
    
    Args:
        album_dir: 专辑目录路径
        api_cache: API 缓存
        options: 选项字典
    
    Returns:
        dict: 统计信息
    """
    if api_cache is None:
        api_cache = AlbumMetadataCache()
    
    if options is None:
        options = {
            "overwrite": True,
            "verbose": False
        }
    
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
    
    # 扫描音频文件（FLAC 和 OGG）
    audio_files = []
    for root, dirs, files in os.walk(album_dir):
        for file in files:
            # 只处理支持的音频格式
            if file.lower().endswith(('.flac', '.ogg')):
                audio_files.append(os.path.join(root, file))
    
    if not audio_files:
        logger.warning(f"目录中没有支持的音频文件（.flac/.ogg）: {album_dir}")
    
    # 处理所有音频文件（FLAC 和 OGG）
    
    stats["total"] = len(audio_files)
    logger.info(f"找到 {len(audio_files)} 个 FLAC 文件")
    
    # 从第一个文件获取专辑信息
    first_audio = audio_files[0]
    tags = extract_audio_tags(first_audio)
    artist = tags.get("artist")
    album = tags.get("album")
    
    if not artist or not album:
        logger.warning(f"缺少必要的标签: {first_audio}")
        stats["skipped"] = len(audio_files)
        return stats
    
    logger.info(f"专辑信息: {artist} - {album}")
    
    # 获取专辑信息（带缓存）
    cache_key = AlbumMetadataCache.generate_key(artist, album)
    album_metadata = api_cache.get(cache_key)
    
    if not album_metadata:
        logger.info("查询 API 获取专辑信息...")
        
        # 搜索专辑
        search_result = search_album(artist, album)
        if not search_result:
            logger.warning(f"未找到专辑: {artist} - {album}")
            stats["skipped"] = len(audio_files)
            return stats
        
        albummid = search_result.get("albummid")
        if not albummid:
            logger.warning(f"未找到 albummid")
            stats["skipped"] = len(audio_files)
            return stats
        
        # 获取专辑信息（包含 aDate）
        album_info = get_album_info_with_date(albummid)
        if not album_info:
            logger.warning(f"未找到专辑信息: {albummid}")
            stats["skipped"] = len(audio_files)
            return stats
        
        # 下载封面
        cover_data = download_cover(albummid, size="500x500")
        cover_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
        
        # 构建缓存数据
        album_metadata = {
            "albummid": albummid,
            "artist": search_result.get("singername"),
            "album": search_result.get("albumname"),
            "pub_year": album_info.get("pub_year", ""),
            "pub_date": album_info.get("pub_date", ""),
            "cover_data": cover_data,
            "cover_url": cover_url
        }
        
        # 写入缓存
        api_cache.set(cache_key, album_metadata)
        logger.info(f"专辑信息已缓存")
    else:
        logger.info("使用缓存的专辑信息")
    
    # 提取信息
    pub_year = album_metadata.get("pub_year", "")
    cover_data = album_metadata.get("cover_data")
    
    if not pub_year:
        logger.warning("未找到发行年份")
    
        track_number = extract_track_number_from_filename(filename)
    
    # 处理所有音频文件（FLAC 和 OGG）
    for i, audio_file in enumerate(audio_files):
        filename = os.path.basename(audio_file)
        logger.info(f"[INFO] 处理文件 {i+1}/{len(audio_files)}: {filename}")
        
        # 提取并添加音轨号
        filename = os.path.basename(audio_file)
        track_number = extract_track_number_from_filename(filename)
        
        # 提取标签
        tags = extract_audio_tags(audio_file)
        artist = tags.get("artist")
        album = tags.get("album")
        
        # 嵌入元数据
        filename = os.path.basename(audio_file)
        track_number = extract_track_number_from_filename(filename)
        success = embed_metadata_to_audio(audio_file, pub_year, cover_data, track_number)
        
        if success:
            stats["success"] += 1
            logger.info(f"[OK] {filename}")
        else:
            stats["failed"] += 1
            logger.warning(f"[FAIL] {filename}")
    
    # 保存封面到音频文件所在的目录（专辑子目录）
    if cover_data:
        # 获取第一个音频文件所在的目录（专辑子目录）
        first_audio_dir = os.path.dirname(audio_files[0])
        cover_path = save_cover_to_directory(first_audio_dir, cover_data)
        logger.info(f"封面已保存到: {cover_path}")

    return stats

if __name__ == '__main__':
    # 获取命令行参数
    if len(sys.argv) > 1:
        album_dir = sys.argv[1]
        print(f'处理专辑目录: {album_dir}')
    else:
        print('用法: python supplement_album_metadata.py <专辑目录>')
        sys.exit(1)
    
    # 处理专辑目录
    stats = process_album_directory(album_dir, api_cache=None, options={'overwrite': True})
    
    # 打印统计信息
    print()
    print('='*50)
    print('处理完成')
    print('='*50)
    print()
    print(f'总文件数: {stats.get("total", 0)}')
    print(f'成功: {stats.get("success", 0)}')
    print(f'失败: {stats.get("failed", 0)}')
    print(f'跳过: {stats.get("skipped", 0)}')
    print('='*50)
    print()
