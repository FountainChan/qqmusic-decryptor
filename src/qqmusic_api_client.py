#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2026 FountainChan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
QQ音乐 API 客户端模块
用于获取专辑信息、封面和发行年份
"""

import requests
import time
import os
import logging
from typing import Dict, Optional, Tuple

# 配置日志
logger = logging.getLogger(__name__)


class QQMusicAPIClient:
    """QQ音乐 API 客户端"""

    def __init__(self, base_url: str = "http://192.168.110.194:3200", timeout: int = 10):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_album(self, artist: str, album_name: str) -> Optional[Dict]:
        """
        搜索专辑获取 ID
        
        Args:
            artist: 歌手名
            album_name: 专辑名
        
        Returns:
            包含 albummid, singermid 等信息的字典，失败返回 None
        """
        try:
            search_key = f"{artist} {album_name}".strip()
            
            response = self.session.get(
                f"{self.base_url}/getSearchByKey",
                params={
                    "key": search_key,
                    "remoteplace": "album",
                    "page": 1,
                    "limit": 10
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "response" not in data or "data" not in data["response"]:
                logger.error(f"搜索失败：无返回数据 - {search_key}")
                return None
            
            songs = data["response"]["data"]["song"]["list"]
            if not songs:
                logger.warning(f"未找到专辑：{search_key}")
                return None
            
            # 返回第一个匹配项
            first_match = songs[0]
            return {
                "albummid": first_match.get("albummid"),
                "singermid": first_match.get("singermid"),
                "albumname": first_match.get("albumname"),
                "singername": first_match.get("singername")
            }
        
        except requests.exceptions.Timeout:
            logger.error(f"搜索专辑超时：{artist} - {album_name}")
            return None
        except Exception as e:
            logger.error(f"搜索专辑异常 {artist} - {album_name}: {e}")
            return None

    def get_album_info(self, albummid: str) -> Optional[Dict]:
        """
        获取专辑详细信息
        
        Args:
            albummid: 专辑 ID
        
        Returns:
            包含专辑详细信息的字典，失败返回 None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/getAlbumInfo",
                params={"albummid": albummid},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "response" not in data or "data" not in data["response"]:
                logger.error(f"获取专辑信息失败：{albummid}")
                return None
            
            album_info = data["response"]["data"]["list"][0]
            
            # 处理发行时间
            pub_time = album_info.get("pub_time")
            if pub_time:
                pub_time_str = str(pub_time)
                pub_year = pub_time_str[:4] if len(pub_time_str) >= 4 else ""
                pub_date = f"{pub_time_str[:4]}-{pub_time_str[4:6]}-{pub_time_str[6:8]}" if len(pub_time_str) >= 8 else pub_year
            else:
                pub_year = ""
                pub_date = ""
            
            return {
                "albumname": album_info.get("albumname"),
                "singername": album_info.get("singername"),
                "pub_time": pub_time,
                "pub_year": pub_year,
                "pub_date": pub_date,
                "genre": album_info.get("genre"),
                "language": album_info.get("language"),
                "desc": album_info.get("desc")
            }
        
        except requests.exceptions.Timeout:
            logger.error(f"获取专辑信息超时：{albummid}")
            return None
        except Exception as e:
            logger.error(f"获取专辑信息异常 {albummid}: {e}")
            return None

    def get_album_cover_url(self, albummid: str, size: str = "500x500") -> Optional[str]:
        """
        获取专辑封面 URL
        
        Args:
            albummid: 专辑 ID
            size: 图片尺寸（300x300, 500x500, 800x800, 1000x1000）
        
        Returns:
            图片 URL，失败返回 None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/getImageUrl",
                params={
                    "id": albummid,
                    "size": size
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "response" not in data or "data" not in data["response"]:
                logger.error(f"获取封面 URL 失败：{albummid}")
                return None
            
            return data["response"]["data"]["imageUrl"]
        
        except Exception as e:
            logger.error(f"获取封面 URL 异常 {albummid}: {e}")
            return None

    def download_album_cover(self, albummid: str, dest_path: str, size: str = "500x500") -> bool:
        """
        下载专辑封面到指定路径
        
        Args:
            albummid: 专辑 ID
            dest_path: 目标文件路径
            size: 图片尺寸
        
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            # 方式1：使用 API 获取 URL
            image_url = self.get_album_cover_url(albummid, size)
            
            if not image_url:
                # 方式2：使用直接 URL 格式
                image_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
                logger.warning(f"API 获取封面失败，使用直接 URL: {image_url}")
            
            logger.info(f"下载封面: {image_url}")
            
            # 下载图片
            response = self.session.get(image_url, timeout=self.timeout)
            response.raise_for_status()
            
            # 确保目标目录存在
            dest_dir = os.path.dirname(dest_path)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            # 写入文件
            with open(dest_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"封面已保存: {dest_path}")
            return True
        
        except Exception as e:
            logger.error(f"下载封面失败 {albummid}: {e}")
            return None
 
    def get_album_info_with_date(self, albummid: str) -> Optional[Dict]:
        """
        获取专辑详细信息（使用 aDate 字段）
        
        Args:
            albummid: 专辑 ID
        
        Returns:
            包含专辑详细信息的字典，失败返回 None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/getAlbumInfo",
                params={"albummid": albummid},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "response" not in data or "data" not in data["response"]:
                logger.error(f"获取专辑信息失败：{albummid}")
                return None
            
            album_info = data["response"]["data"]["list"][0]
            
            # 直接从 data 层级获取 aDate 字段
            a_date = data["response"]["data"].get("aDate")
            
            # 处理日期
            pub_year = ""
            pub_date = ""
            
            if a_date:
                a_date_str = str(a_date)
                pub_year = a_date_str[:4] if len(a_date_str) >= 4 else ""
                pub_date = a_date_str  # 完整日期 "2015-06-11"
                logger.info(f"找到 aDate: {a_date}")
            else:
                # 备用方案：从 album_info 的 albumdesc 中提取日期
                album_desc = album_info.get("albumdesc", "")
                if album_desc:
                    import re
                    match = re.search(r'(\d{4})年', album_desc)
                    if match:
                        pub_year = match.group(1)
                        logger.info(f"从描述中提取年份: {pub_year}")
            
            return {
                "albumname": album_info.get("albumname"),
                "singername": album_info.get("singername"),
                "pub_time": a_date,  # 保存原始日期
                "pub_year": pub_year,   # 提取的年份
                "pub_date": pub_date,   # 完整日期
                "genre": album_info.get("genre"),
                "language": album_info.get("language"),
                "desc": album_info.get("desc")
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"获取专辑信息超时：{albummid}")
            return None
        except Exception as e:
            logger.error(f"获取专辑信息异常 {albummid}: {e}")
            return None
 
    def download_cover_data(self, albummid: str, size: str = "500x500") -> Optional[bytes]:
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
            image_url = self.get_album_cover_url(albummid, size)
            
            if not image_url:
                # 方式2：使用直接 URL
                image_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
                logger.warning(f"API 获取封面失败，使用直接 URL: {image_url}")
            
            logger.info(f"下载封面: {image_url}")
            
            # 下载图片
            response = self.session.get(image_url, timeout=self.timeout)
            response.raise_for_status()
            
            cover_data = response.content
            logger.info(f"封面数据大小: {len(cover_data)} bytes")
            return cover_data
        
        except Exception as e:
            logger.error(f"下载封面失败 {albummid}: {e}")
            return None
 
class AlbumMetadataCache:
    """专辑元数据缓存，避免重复请求"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str) -> Optional[Dict]:
        """从缓存获取专辑信息"""
        return self.cache.get(key)
    
    def set(self, key: str, data: Dict):
        """设置缓存"""
        self.cache[key] = data
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    @staticmethod
    def generate_key(artist: str, album: str) -> str:
        """生成缓存键"""
        return f"{artist}::{album}"


# 全局缓存实例（单例模式）
_global_cache = AlbumMetadataCache()


def get_album_metadata_cached(api_client: QQMusicAPIClient, artist: str, album: str) -> Optional[Dict]:
    """
    获取专辑元数据（带缓存）
    
    Args:
        api_client: API 客户端实例
        artist: 歌手名
        album: 专辑名
    
    Returns:
        包含 albummid, cover_data, pub_year 等信息的字典
    """
    cache_key = AlbumMetadataCache.generate_key(artist, album)
    
    # 检查缓存
    cached_data = _global_cache.get(cache_key)
    if cached_data:
        logger.info(f"使用缓存的专辑信息: {artist} - {album}")
        return cached_data
    
    # 搜索专辑
    search_result = api_client.search_album(artist, album)
    if not search_result:
        return None
    
    albummid = search_result.get("albummid")
    if not albummid:
        logger.error(f"未找到 albummid: {artist} - {album}")
        return None
    
    # 获取详细信息（使用修复后的 aDate 字段）
    album_info = api_client.get_album_info_with_date(albummid)
    if not album_info:
        return None
    
    # 提取年份和日期
    pub_year = album_info.get("pub_year", "")
    pub_date = album_info.get("pub_date", "")
    
    # 下载封面数据（使用新的方法）
    cover_data = api_client.download_cover_data(albummid, size="500x500")
    cover_url = api_client.get_album_cover_url(albummid, size="500x500")
    
    # 构建返回数据
    metadata = {
        "albummid": albummid,
        "artist": search_result.get("singername"),
        "album": search_result.get("albumname"),
        "pub_year": pub_year,  # 从 aDate 提取的年份
        "pub_date": pub_date,  # 完整的 aDate
        "genre": album_info.get("genre"),
        "language": album_info.get("language"),
        "cover_data": cover_data,
        "cover_url": cover_url
    }
    
    # 写入缓存
    _global_cache.set(cache_key, metadata)
    
    return metadata
