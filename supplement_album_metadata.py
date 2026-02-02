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
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'supplement_album_metadata.log')

# 默认只输出到文件
handlers = [logging.FileHandler(log_file, encoding='utf-8')]

# 根据命令行参数决定是否输出到控制台
if '--verbose' in sys.argv or '-v' in sys.argv:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    handlers.append(console_handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers,
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
        artist_list = audio.get("ARTIST", [""])
        artist = artist_list[0] if artist_list else ""
        
        album_list = audio.get("ALBUM", [""])
        album = album_list[0] if album_list else ""
        
        title_list = audio.get("TITLE", [""])
        title = title_list[0] if title_list else ""
        
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


def write_track_number(audio_file_path, track_number):
    """
    写入音轨号到音频文件（不依赖 API）
    
    Args:
        audio_file_path: 音频文件路径
        track_number: 音轨号（整数）
    
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        if audio_file_path.lower().endswith('.flac'):
            audio = FLAC(audio_file_path)
            
            # 检查是否已经有音轨号
            existing_track = audio.get("TRACKNUMBER")
            if existing_track:
                logger.info(f"FLAC 文件已经有音轨号: {existing_track}，跳过写入")
                return True  # 跳过，但不算失败
            
            # 写入音轨号
            audio["TRACKNUMBER"] = str(track_number)
            audio.save()
            logger.info(f"写入音轨号 (FLAC): {track_number}")
            return True
            
        elif audio_file_path.lower().endswith('.ogg'):
            from mutagen.oggvorbis import OggVorbis
            audio = OggVorbis(audio_file_path)
            
            # 检查是否已经有音轨号
            existing_track = audio.get("TRACKNUMBER")
            if existing_track:
                logger.info(f"OGG 文件已经有音轨号: {existing_track}，跳过写入")
                return True  # 跳过，但不算失败
            
            # 写入音轨号
            audio["TRACKNUMBER"] = str(track_number)
            audio.save()
            logger.info(f"写入音轨号 (OGG): {track_number}")
            return True
            
        else:
            logger.warning(f"不支持的格式: {audio_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"写入音轨号失败 {audio_file_path}: {e}")
        return False


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


def embed_year_and_cover(audio_file_path, pub_year, cover_data):
    """
    嵌入年份和封面到音频文件（依赖 API）
    
    Args:
        audio_file_path: 音频文件路径
        pub_year: 发行年份（字符串）
        cover_data: 封面数据（字节）
    
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
            
            # OGG 文件不嵌入封面
            
            # 保存
            audio.save()
            logger.info(f"保存元数据 (OGG): {os.path.basename(audio_file_path)}")
            return True
            
        else:
            # 不支持的格式
            logger.error(f"不支持的文件格式: {audio_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"嵌入年份和封面失败 {audio_file_path}: {e}")
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
    处理整个专辑目录（所有 FLAC 和 OGG 文件）
    按子目录逐个处理
    
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
    
    # 维度1：文件级统计
    file_stats = {
        "total": 0,           # 总音频文件数
        "processed": 0,       # 成功处理年份/封面的文件数
        "unchanged": 0,       # 无需修改的文件数（已有或无数据）
        "failed": 0           # 处理失败的文件数
    }

    # 维度2：操作级统计（简化版，不包含音轨号）
    operation_stats = {
        "year_cover": {
            "success": 0,     # 成功写入年份和/或封面
            "skipped": 0,     # 无API数据跳过
            "failed": 0       # 写入失败
        },
        "cover_saved": {
            "saved": 0,      # 成功保存cover.jpg的专辑目录数
            "failed": 0       # 保存失败的目录数
        }
    }

    # 保留stats变量用于向后兼容
    stats = {
        "total_files": 0,
        "processed_files": 0,
        "unchanged_files": 0,
        "failed_files": 0
    }
    
    logger.info(f"正在处理专辑目录: {album_dir}")
    
    # 第一次遍历：收集所有音频文件，按目录分组
    dir_audio_files = {}  # {目录路径: [音频文件列表]}
    
    for root, dirs, files in os.walk(album_dir):
        for file in files:
            if file.lower().endswith(('.flac', '.ogg')):
                file_path = os.path.join(root, file)
                if root not in dir_audio_files:
                    dir_audio_files[root] = []
                dir_audio_files[root].append(file_path)
    
    if not dir_audio_files:
        logger.warning(f"目录中没有支持的音频文件（.flac/.ogg）: {album_dir}")
        return stats
    
    # 计算总文件数
    total_files = sum(len(files) for files in dir_audio_files.values())
    file_stats["total"] = total_files  # 设置总文件数
    logger.info(f"找到 {len(dir_audio_files)} 个子目录，共 {total_files} 个音频文件")
    
    # 第二次遍历：按子目录逐个处理
    for dir_path, audio_files in sorted(dir_audio_files.items()):
        rel_dir = os.path.relpath(dir_path, album_dir)
        logger.info(f"正在处理专辑目录: {dir_path}: {len(audio_files)} 个文件")
        
        if not audio_files:
            logger.warning(f"专辑目录中没有音频文件: {dir_path}")
            continue
        
        # 从第一个文件获取专辑信息
        first_audio = audio_files[0]
        tags = extract_audio_tags(first_audio)
        artist = tags.get("artist")
        album = tags.get("album")
        
        if not artist or not album:
            logger.warning(f"缺少必要的标签: {first_audio}")
            stats["skipped"] += len(audio_files)
            continue
        
        logger.info(f"专辑信息: {artist} - {album}")
        
        # 获取专辑信息（带缓存）
        cache_key = AlbumMetadataCache.generate_key(artist, album)
        album_metadata = api_cache.get(cache_key)
        pub_year = None
        cover_data = None
        
        if not album_metadata:
            logger.info("查询 API 获取专辑信息...")
            
            try:
                # 搜索专辑
                search_result = search_album(artist, album)
                if not search_result:
                    logger.warning(f"未找到专辑: {artist} - {album}")
                    pub_year = None
                    cover_data = None
                else:
                    albummid = search_result.get("albummid")
                    if not albummid:
                        logger.warning("未找到 albummid")
                        logger.warning("年份和封面处理将被跳过，但音轨号仍然会处理")
                        pub_year = None
                        cover_data = None
                    else:
                        # 获取专辑信息（包含 aDate）
                        album_info = get_album_info_with_date(albummid)
                        if not album_info:
                            logger.warning(f"未找到专辑信息: {albummid}")
                            pub_year = None
                            cover_data = None
                        else:
                            # 提取年份
                            pub_year = album_info.get("pub_year", "")
                            
                            # 下载封面
                            cover_data = download_cover(albummid, size="500x500")
                            cover_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
                            
                            # 构建缓存数据
                            album_metadata = {
                                "albummid": albummid,
                                "artist": search_result.get("singername"),
                                "album": search_result.get("albumname"),
                                "pub_year": pub_year,
                                "pub_date": album_info.get("pub_date", ""),
                                "cover_data": cover_data,
                                "cover_url": cover_url
                            }
                            
                            # 写入缓存
                            api_cache.set(cache_key, album_metadata)
                            logger.info(f"专辑信息已缓存")
            except Exception as e:
                logger.error(f"API 调用异常: {e}")
                logger.warning("年份和封面处理将被跳过，但音轨号仍然会处理")
                pub_year = None
                cover_data = None
        else:
            logger.info("使用缓存的专辑信息")
            # 提取缓存的年份和封面
            pub_year = album_metadata.get("pub_year", "")
            cover_data = album_metadata.get("cover_data")
        
        # 如果没有获取到年份和封面
        if not pub_year and not cover_data:
            logger.warning("未找到年份和封面数据")
            logger.info("年份和封面处理将被跳过，但音轨号仍然会处理")
        
        # 处理该专辑目录的所有音频文件
        for i, audio_file in enumerate(audio_files):
            filename = os.path.basename(audio_file)
            logger.info(f"[INFO] 处理文件 {i+1}/{len(audio_files)}: {filename}")
            
            # 步骤 1：音轨号处理（不依赖 API，不统计）
            track_number = extract_track_number_from_filename(filename)
            if track_number is not None:
                # 写入音轨号，但不计入统计
                write_track_number(audio_file, track_number)
                logger.info(f"[OK] 音轨号: {track_number}")
            else:
                logger.warning("[SKIP] 未找到音轨号")
            
            # 步骤 2：年份和封面处理（依赖 API，可能为 None）
            metadata_processed = False  # 标记是否处理了年份或封面

            if pub_year or cover_data:
                try:
                    success = embed_year_and_cover(audio_file, pub_year, cover_data)
                    if success:
                        operation_stats["year_cover"]["success"] += 1
                        metadata_processed = True
                        logger.info(f"[OK] {filename}")
                    else:
                        operation_stats["year_cover"]["failed"] += 1
                        file_stats["failed"] += 1
                        logger.warning(f"[FAIL] {filename}")
                except Exception as e:
                    logger.error(f"嵌入年份和封面失败 {filename}: {e}")
                    operation_stats["year_cover"]["failed"] += 1
                    file_stats["failed"] += 1
            else:
                operation_stats["year_cover"]["skipped"] += 1
                logger.info("[SKIP] 没有年份和封面数据")

            # 文件级统计
            if metadata_processed:
                file_stats["processed"] += 1
            else:
                file_stats["unchanged"] += 1

        # 保存封面到专辑目录
        if cover_data:
            cover_path = save_cover_to_directory(dir_path, cover_data)
            if cover_path:
                operation_stats["cover_saved"]["saved"] += 1
                logger.info(f"封面已保存到: {cover_path}")
            else:
                operation_stats["cover_saved"]["failed"] += 1
                logger.error(f"封面保存失败")
    
    # 合并两个统计维度
    combined_stats = {
        "file_stats": file_stats,
        "operation_stats": operation_stats,
        # 保留stats用于向后兼容
        "stats": stats
    }
    return combined_stats

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='专辑元数据补充工具')
    parser.add_argument('album_dir', help='专辑目录')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际修改文件')

    args = parser.parse_args()

    album_dir = args.album_dir
    verbose = args.verbose
    dry_run = args.dry_run

    # 处理专辑目录
    if not os.path.exists(album_dir):
        print(f'错误: 目录不存在: {album_dir}')
        sys.exit(1)

    print(f'处理专辑目录: {album_dir}')
    logger.info(f'处理专辑目录: {album_dir}')

    if dry_run:
        print(f"[DRY RUN] 将处理目录: {album_dir}")
        print(f"[DRY RUN] 不实际修改文件")
        combined_stats = None
    else:
        combined_stats = process_album_directory(album_dir, api_cache=None, options={'overwrite': True})
        file_stats = combined_stats["file_stats"]
        operation_stats = combined_stats["operation_stats"]

    # 输出统计信息
    if combined_stats:
        logger.info('='*50)
        logger.info('处理完成')
        logger.info('='*50)
        logger.info('')
        logger.info(f'总文件数: {file_stats["total"]}')
        logger.info(f'成功处理: {file_stats["processed"]}')
        logger.info(f'无需修改: {file_stats["unchanged"]}')
        logger.info(f'处理失败: {file_stats["failed"]}')
        logger.info('')
        logger.info('-'*50)
        logger.info('操作级别统计:')
        logger.info('-'*50)
        logger.info(f'年份和封面: 成功 {operation_stats["year_cover"]["success"]}, '
                    f'跳过 {operation_stats["year_cover"]["skipped"]}, '
                    f'失败 {operation_stats["year_cover"]["failed"]}')
        logger.info(f'封面保存: 保存 {operation_stats["cover_saved"]["saved"]}, '
                    f'失败 {operation_stats["cover_saved"]["failed"]}')
        logger.info('='*50)
        logger.info('')
