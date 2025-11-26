#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ModVersion:
    """MOD 版本信息"""

    version_number: str
    version_id: str
    game_versions: List[str]
    loaders: List[str]
    maven_url: Optional[str] = None


@dataclass
class ModInfo:
    """MOD 基本信息"""

    project_id: str
    slug: str
    title: str
    description: str
    client_side: str
    server_side: str
    versions: List[ModVersion]
