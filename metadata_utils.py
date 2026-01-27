#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FLAC 元数据处理工具模块
用于为 FLAC 文件添加音轨号等元数据
"""

import re
import os
import logging
from mutagen.flac import FLAC, FLACNoHeaderError

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

        # 检查是否是FLAC文件
        if not flac_file_path.lower().endswith('.flac'):
            logger.error(f"不是FLAC文件: {flac_file_path}")
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
