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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metadata_utils import extract_track_number_from_filename
from abc import ABC, abstractmethod
from pathlib import Path
import logging

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'supplement_album_metadata.log')

# 默认输出到控制台和文件
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
handlers = [
    logging.FileHandler(log_file, encoding='utf-8'),
    console_handler
]

# 如果指定 --quiet，则只输出到文件
if '--quiet' in sys.argv or '-q' in sys.argv:
    handlers = [logging.FileHandler(log_file, encoding='utf-8')]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers,
    force=True
)
logger = logging.getLogger(__name__)

# API 配置
QQ_MUSIC_API_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"
COVER_URL_TEMPLATE = "https://y.gtimg.cn/music/photo_new/T002R{size}M000{album_mid}.jpg?max_age=2592000"
API_HEADERS = {"Referer": "https://y.qq.com/"}
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


class AudioMetadataExtractor(ABC):
    """音频元数据提取器抽象基类"""

    @abstractmethod
    def extract_tags(self, file_path: str):
        """提取文件标签"""
        pass

    @abstractmethod
    def load_audio(self, file_path: str):
        """加载音频文件（返回音频对象）"""
        pass

    @abstractmethod
    def embed_cover(self, audio, cover_data: bytes):
        """嵌入封面数据"""
        pass


class FLACExtractor(AudioMetadataExtractor):
    """FLAC 文件元数据提取器"""

    def extract_tags(self, file_path: str):
        """提取 FLAC 文件标签"""
        audio = FLAC(file_path)
        return {
            "artist": audio["ARTIST"][0],
            "album": audio["ALBUM"][0],
            "title": audio["TITLE"][0]
        }

    def load_audio(self, file_path: str):
        """加载音频文件"""
        return FLAC(file_path)

    def embed_cover(self, audio, cover_data: bytes):
        """嵌入封面到 FLAC 文件"""
        image = Picture()
        image.type = 3
        image.mime = "image/jpeg"
        image.data = cover_data
        audio.add_picture(image)


class OGGExtractor(AudioMetadataExtractor):
    """OGG 文件元数据提取器"""

    def extract_tags(self, file_path: str):
        """提取 OGG 文件标签"""
        audio = OggVorbis(file_path)
        return {
            "artist": audio["ARTIST"][0] or "",
            "album": audio["ALBUM"][0] or "",
            "title": audio["TITLE"][0] or ""
        }

    def load_audio(self, file_path: str):
        """加载音频文件"""
        return OggVorbis(file_path)

    def embed_cover(self, audio, cover_data: bytes):
        """OGG 文件不支持封面嵌入（只保存为独立文件）"""
        pass


def get_extractor(file_path: str) -> AudioMetadataExtractor:
    """根据文件类型获取对应的提取器"""
    ext = Path(file_path).suffix.lower()
    extractors = {'.flac': FLACExtractor, '.ogg': OGGExtractor}
    extractor_class = extractors.get(ext)
    if not extractor_class:
        raise ValueError(f"不支持的文件格式: {ext}")
    return extractor_class()


def extract_audio_tags(audio_file_path: str) -> dict:
    """提取音频文件标签（统一接口）"""
    try:
        extractor = get_extractor(audio_file_path)
        return extractor.extract_tags(audio_file_path)
    except Exception as e:
        logger.error(f"读取标签失败 {audio_file_path}: {e}")
        return {"artist": "", "album": "", "title": ""}


def search_album(artist, album):
    """
    搜索专辑获取 albummid（使用 QQ 音乐官方 API）

    Args:
        artist: 歌手名
        album: 专辑名

    Returns:
        dict: {'albummid': str, 'singername': str, 'albumname': str}
    """
    try:
        search_key = f"{artist} {album}".strip()

        payload = {
            "music.search.SearchCgiService": {
                "module": "music.search.SearchCgiService",
                "method": "DoSearchForQQMusicDesktop",
                "param": {
                    "search_type": 0,
                    "query": search_key,
                    "page_num": 1,
                    "num_per_page": 10
                }
            }
        }

        response = requests.post(
            QQ_MUSIC_API_URL,
            json=payload,
            headers=API_HEADERS,
            timeout=API_TIMEOUT
        )
        response.raise_for_status()

        data = response.json()

        search_service = data.get("music.search.SearchCgiService", {})
        if search_service.get("code") != 0:
            logger.error(f"搜索失败：返回码 {search_service.get('code')}")
            return None

        songs = (search_service.get("data", {})
                 .get("body", {})
                 .get("song", {})
                 .get("list", []))
        if not songs:
            logger.warning(f"未找到专辑：{search_key}")
            return None

        first_song = songs[0]
        album_info = first_song.get("album", {})
        singer_list = first_song.get("singer", [{}])

        return {
            "albummid": album_info.get("mid"),
            "singername": singer_list[0].get("name", "") if singer_list else "",
            "albumname": album_info.get("name", "")
        }

    except Exception as e:
        logger.error(f"搜索专辑异常: {e}")
        return None


def download_cover(albummid, size="500x500"):
    """
    下载专辑封面数据

    Args:
        albummid: 专辑 mid
        size: 图片尺寸

    Returns:
        bytes: 封面图片数据，失败返回 None
    """
    try:
        cover_url = COVER_URL_TEMPLATE.format(size=size, album_mid=albummid)
        logger.info(f"下载封面: {cover_url}")

        response = requests.get(cover_url, headers=API_HEADERS, timeout=REQUEST_TIMEOUT)
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
        extractor = get_extractor(audio_file_path)

        if isinstance(extractor, FLACExtractor):
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

        elif isinstance(extractor, OGGExtractor):
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
        extractor = get_extractor(audio_file_path)
        audio = extractor.load_audio(audio_file_path)

        # 添加年份（DATE 标签）
        if pub_year:
            audio["DATE"] = pub_year
            logger.info(f"添加年份: {pub_year}")

        # 添加音轨号（TRACKNUMBER 标签）
        if track_number is not None:
            existing_track = audio.get("TRACKNUMBER")
            if existing_track:
                logger.info(f"文件已经有音轨号: {existing_track}，跳过写入")
            else:
                audio["TRACKNUMBER"] = str(track_number)
                logger.info(f"添加音轨号: {track_number}")
        else:
            logger.warning(f"未找到音轨号，跳过音轨号写入")

        # 添加封面（PICTURE 标签）
        if cover_data:
            extractor.embed_cover(audio, cover_data)
            logger.info(f"嵌入封面")

        # 保存
        audio.save()
        logger.info(f"保存元数据: {os.path.basename(audio_file_path)}")
        return True

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


def collect_audio_files_by_directory(album_dir: str) -> dict:
    """收集并分组音频文件"""
    dir_audio_files = {}

    for root, dirs, files in os.walk(album_dir):
        for file in files:
            if file.lower().endswith(('.flac', '.ogg')):
                file_path = os.path.join(root, file)
                dir_audio_files.setdefault(root, []).append(file_path)

    return dir_audio_files


def get_album_data(artist, album, api_cache):
    """获取专辑数据（带缓存）"""
    cache_key = AlbumMetadataCache.generate_key(artist, album)
    album_metadata = api_cache.get(cache_key)

    if not album_metadata:
        logger.info("查询 API 获取专辑信息...")

        try:
            # 搜索专辑
            search_result = search_album(artist, album)
            if not search_result:
                logger.warning(f"未找到专辑: {artist} - {album}")
                return None

            albummid = search_result.get("albummid")
            if not albummid:
                logger.warning("未找到 albummid")
                return None

            # 下载封面
            cover_data = download_cover(albummid, size="500x500")
            cover_url = COVER_URL_TEMPLATE.format(size="500x500", album_mid=albummid)

            # 构建缓存数据
            album_metadata = {
                "albummid": albummid,
                "artist": search_result.get("singername"),
                "album": search_result.get("albumname"),
                "cover_data": cover_data,
                "cover_url": cover_url
            }

            # 写入缓存
            api_cache.set(cache_key, album_metadata)
            logger.info(f"专辑信息已缓存")

        except Exception as e:
            logger.error(f"API 调用异常: {e}")
            return None
    else:
        logger.info("使用缓存的专辑信息")

    return album_metadata


def process_single_file(audio_file_path, pub_year, cover_data, track_number=None):
    """处理单个音频文件"""
    filename = os.path.basename(audio_file_path)
    metadata_processed = False

    try:
        # 年份和封面处理
        if pub_year or cover_data:
            success = embed_metadata_to_audio(audio_file_path, pub_year, cover_data, track_number)
            if success:
                metadata_processed = True
                logger.info(f"[OK] {filename}")
            else:
                logger.warning(f"[FAIL] {filename}")
        else:
            logger.info("[SKIP] 没有年份和封面数据")
    except Exception as e:
        logger.error(f"处理文件失败 {filename}: {e}")

    return metadata_processed


def process_directory(dir_path, audio_files, api_cache):
    """处理单个专辑目录"""
    # 从第一个文件获取专辑信息
    first_audio = audio_files[0]
    tags = extract_audio_tags(first_audio)
    artist = tags.get("artist")
    album = tags.get("album")

    if not artist or not album:
        logger.warning(f"缺少必要的标签: {first_audio}")
        return {"dir_path": dir_path, "status": "skipped", "reason": "缺少标签"}

    logger.info(f"专辑信息: {artist} - {album}")

    # 获取专辑数据（带缓存）
    album_metadata = get_album_data(artist, album, api_cache)
    if not album_metadata:
        logger.warning("未获取到专辑信息")
        return {"dir_path": dir_path, "status": "skipped", "reason": "无专辑信息"}

    pub_year = album_metadata.get("pub_year", "")
    cover_data = album_metadata.get("cover_data")

    # 处理该专辑目录的所有音频文件
    file_results = []
    for i, audio_file in enumerate(audio_files):
        filename = os.path.basename(audio_file)
        logger.info(f"[INFO] 处理文件 {i+1}/{len(audio_files)}: {filename}")

        # 步骤1：音轨号处理（不依赖 API）
        track_number = extract_track_number_from_filename(filename)
        if track_number is not None:
            # 写入音轨号，但不计入统计
            write_track_number(audio_file, track_number)
            logger.info(f"[OK] 音轨号: {track_number}")
        else:
            logger.warning("[SKIP] 未找到音轨号")

        # 步骤2：年份和封面处理（依赖 API）
        metadata_processed = False
        if pub_year or cover_data:
            try:
                success = embed_metadata_to_audio(audio_file, pub_year, cover_data, track_number)
                if success:
                    metadata_processed = True
                    logger.info(f"[OK] {filename}")
                else:
                    logger.warning(f"[FAIL] {filename}")
            except Exception as e:
                logger.error(f"嵌入年份和封面失败 {filename}: {e}")
        else:
            logger.info("[SKIP] 没有年份和封面数据")

        file_results.append({
            "file": audio_file,
            "metadata_processed": metadata_processed
        })

    # 保存封面到专辑目录
    if cover_data:
        cover_path = save_cover_to_directory(dir_path, cover_data)
        if not cover_path:
            return {"dir_path": dir_path, "status": "error", "reason": "封面保存失败"}

    return {"dir_path": dir_path, "files": file_results, "album_metadata": album_metadata}


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
    dir_audio_files = collect_audio_files_by_directory(album_dir)

    if not dir_audio_files:
        logger.warning(f"目录中没有支持的音频文件（.flac/.ogg）: {album_dir}")
        return {"file_stats": file_stats, "operation_stats": operation_stats, "stats": stats}

    # 计算总文件数
    total_files = sum(len(files) for files in dir_audio_files.values())
    file_stats["total"] = total_files
    logger.info(f"找到 {len(dir_audio_files)} 个子目录，共 {total_files} 个音频文件")

    # 第二次遍历：按子目录逐个处理
    for dir_path, audio_files in sorted(dir_audio_files.items()):
        logger.info(f"正在处理专辑目录: {dir_path}: {len(audio_files)} 个文件")

        if not audio_files:
            logger.warning(f"专辑目录中没有音频文件: {dir_path}")
            continue

        # 处理单个目录
        result = process_directory(dir_path, audio_files, api_cache)

        if result.get("status") == "skipped":
            file_stats["unchanged"] += len(audio_files)
            continue

        if result.get("status") == "error":
            file_stats["failed"] += len(audio_files)
            continue

        # 统计处理结果
        for file_result in result.get("files", []):
            if file_result.get("metadata_processed"):
                file_stats["processed"] += 1
            else:
                file_stats["unchanged"] += 1

        # 统计封面保存
        album_metadata = result.get("album_metadata", {})
        if album_metadata.get("cover_data"):
            cover_path = save_cover_to_directory(dir_path, album_metadata["cover_data"])
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
