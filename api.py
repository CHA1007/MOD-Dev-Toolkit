#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modrinth API 客户端
"""

import requests
from typing import List, Dict, Optional


class ModrinthAPI:
    """Modrinth API 客户端"""

    BASE_URL = "https://api.modrinth.com/v2"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (MOD-Dev-Toolkit/1.2.0)",
            }
        )

    def search_projects(
        self, query: str, loader: str = "forge", limit: int = 10, offset: int = 0
    ) -> Dict:
        """
        搜索 MOD 项目

        Args:
            query: 搜索关键词（支持中文，但 Modrinth 主要支持英文搜索）
            loader: 模组加载器类型 (forge, fabric, neoforge)
            limit: 返回结果数量
            offset: 偏移量（用于分页）

        Returns:
            包含 hits 和 total 的字典
        """
        url = f"{self.BASE_URL}/search"

        params = {
            "query": query,
            "facets": f'[["project_type:mod"],["categories:{loader}"]]',
            "limit": limit,
            "offset": offset,
        }

        try:
            response = self.session.get(url, params=params)
            response.encoding = "utf-8"
            response.raise_for_status()
            data = response.json()
            return {
                "hits": data.get("hits", []),
                "total": data.get("total_hits", 0),
                "offset": offset,
            }
        except Exception as e:
            print(f"搜索出错: {e}")
            return {"hits": [], "total": 0, "offset": offset}

    def get_project(self, project_id: str) -> Optional[Dict]:
        """
        获取项目详细信息

        Args:
            project_id: 项目 ID 或 slug

        Returns:
            项目信息字典
        """
        url = f"{self.BASE_URL}/project/{project_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取项目信息出错: {e}")
            return None

    def get_project_versions(
        self, project_id: str, game_version: Optional[str] = None, loader: str = "forge"
    ) -> List[Dict]:
        """
        获取项目的所有版本（可筛选）

        Args:
            project_id: 项目 ID 或 slug
            game_version: Minecraft 版本 (如 "1.20.1")
            loader: 模组加载器类型

        Returns:
            版本列表
        """
        url = f"{self.BASE_URL}/project/{project_id}/version"
        params = {}

        if game_version:
            params["game_versions"] = f'["{game_version}"]'
        if loader:
            params["loaders"] = f'["{loader}"]'

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            versions = response.json()
            if not versions:
                print(
                    f"警告: 项目 {project_id} 没有找到匹配的版本 (游戏版本: {game_version or '任意'}, 加载器: {loader})"
                )
            return versions
        except requests.exceptions.HTTPError as e:
            print(f"获取版本列表出错 (HTTP {e.response.status_code}): {e}")
            if e.response.status_code == 404:
                print(f"提示: 项目 {project_id} 可能不存在或已被删除")
            return []
        except Exception as e:
            print(f"获取版本列表出错: {e}")
            return []

    def get_all_project_versions(self, project_id: str) -> List[Dict]:
        """
        获取项目的所有版本（不筛选，用于显示版本列表）

        Args:
            project_id: 项目 ID 或 slug

        Returns:
            版本列表（按发布时间降序排列，已去重）
        """
        url = f"{self.BASE_URL}/project/{project_id}/version"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            versions = response.json()

            if not versions:
                return []

            # 按版本号去重，合并相同版本号的信息
            version_dict = {}
            for v in versions:
                version_number = v.get("version_number", "")
                if not version_number:
                    continue

                if version_number not in version_dict:
                    # 新版本号，直接添加
                    version_dict[version_number] = v.copy()
                else:
                    # 已存在的版本号，合并信息
                    existing = version_dict[version_number]
                    # 合并游戏版本列表（去重）
                    existing_game_versions = set(existing.get("game_versions", []))
                    new_game_versions = set(v.get("game_versions", []))
                    existing["game_versions"] = sorted(
                        list(existing_game_versions | new_game_versions)
                    )

                    # 合并加载器列表（去重）
                    existing_loaders = set(existing.get("loaders", []))
                    new_loaders = set(v.get("loaders", []))
                    existing["loaders"] = sorted(list(existing_loaders | new_loaders))

                    # 保留最新的发布时间
                    existing_date = existing.get("date_published", "")
                    new_date = v.get("date_published", "")
                    if new_date > existing_date:
                        existing["date_published"] = new_date

            # 转换为列表并按发布时间排序（最新的在前）
            unique_versions = list(version_dict.values())
            unique_versions.sort(
                key=lambda x: x.get("date_published", ""), reverse=True
            )

            return unique_versions
        except requests.exceptions.HTTPError as e:
            print(f"获取版本列表出错 (HTTP {e.response.status_code}): {e}")
            if e.response.status_code == 404:
                print(f"提示: 项目 {project_id} 可能不存在或已被删除")
            return []
        except Exception as e:
            print(f"获取版本列表出错: {e}")
            return []
