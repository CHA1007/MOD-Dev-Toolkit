#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖配置生成器
"""

from typing import Dict, Optional
from api import ModrinthAPI


class ForgeDepGenerator:
    """Forge MOD 依赖代码生成器"""

    def __init__(self, api: ModrinthAPI):
        self.api = api

    def generate_gradle_dependency(
        self,
        project_id: str,
        version: str = "latest",
        game_version: Optional[str] = None,
        loader: str = "forge",
        dependency_type: str = "implementation",
        mod_version: Optional[str] = None,
    ) -> str:
        """
        生成 build.gradle 依赖配置

        Args:
            project_id: MOD 项目 ID 或 slug
            version: 版本号或 "latest"（已弃用，使用 mod_version）
            game_version: Minecraft 版本
            loader: 模组加载器类型 (forge, fabric, neoforge)
            dependency_type: 依赖类型 (implementation, compileOnly, runtimeOnly, api)
            mod_version: MOD 版本号（如果为 None 则使用最新版本）

        Returns:
            Gradle 依赖配置代码
        """
        project = self.api.get_project(project_id)
        if not project:
            return f"// 错误: 无法获取项目 {project_id} 的信息"

        versions = self.api.get_project_versions(project_id, game_version, loader)
        if not versions:
            return f"// 错误: 项目 {project['title']} 没有可用版本（游戏版本: {game_version or '任意'}, 加载器: {loader}）"

        # 选择版本：如果指定了 mod_version，查找匹配的版本；否则使用最新版本
        selected_version = None
        if mod_version:
            # 查找匹配的版本号
            for v in versions:
                if v.get("version_number") == mod_version:
                    selected_version = v
                    break
            if not selected_version:
                # 如果找不到精确匹配，使用最新版本并提示
                selected_version = versions[0]
                print(
                    f"警告: 未找到版本 {mod_version}，使用最新版本 {selected_version['version_number']}"
                )
        else:
            # 使用最新版本
            selected_version = versions[0]

        # 验证依赖类型
        valid_types = ["implementation", "compileOnly", "runtimeOnly", "api"]
        if dependency_type not in valid_types:
            dependency_type = "implementation"

        # 根据加载器类型选择不同的依赖格式
        version_number = selected_version["version_number"]
        if loader.lower() == "neoforge":
            # NeoForge 使用标准的依赖格式
            dependency_line = f'    {dependency_type} "maven.modrinth:{project["slug"]}:{version_number}"'
        elif loader.lower() == "fabric":
            # Fabric 也使用标准的依赖格式
            dependency_line = f'    {dependency_type} "maven.modrinth:{project["slug"]}:{version_number}"'
        else:
            # Forge 使用 fg.deobf 格式（仅对 implementation 和 api 类型）
            if dependency_type in ["implementation", "api"]:
                dependency_line = f'    {dependency_type} fg.deobf("maven.modrinth:{project["slug"]}:{version_number}")'
            else:
                # compileOnly 和 runtimeOnly 不使用 fg.deobf
                dependency_line = f'    {dependency_type} "maven.modrinth:{project["slug"]}:{version_number}"'

        # 构建 Gradle 依赖代码
        gradle_code = f"""// {project["title"]}
// 描述: {project["description"]}
// MOD 版本: {version_number}
dependencies {{
    // Modrinth Maven ({dependency_type})
{dependency_line}
}}

// 如果还没有添加 Modrinth Maven 仓库，请在 repositories 块中添加:
repositories {{
    maven {{
        name = "Modrinth"
        url = "https://api.modrinth.com/maven"
    }}
}}
"""
        return gradle_code

    def format_version_info(self, version: Dict) -> str:
        """
        格式化版本信息用于显示

        Args:
            version: 版本字典

        Returns:
            格式化的版本信息字符串
        """
        version_number = version.get("version_number", "未知")
        date_published = version.get("date_published", "")
        game_versions = version.get("game_versions", [])
        loaders = version.get("loaders", [])
        version_type = version.get("version_type", "release")

        # 格式化日期
        if date_published:
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(date_published.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_date = date_published
        else:
            formatted_date = "未知"

        info = f"版本号: {version_number}\n"
        info += f"发布时间: {formatted_date}\n"
        info += f"类型: {version_type}\n"
        info += (
            f"游戏版本: {', '.join(game_versions[:5])}"
            + (f" 等{len(game_versions)}个" if len(game_versions) > 5 else "")
            + "\n"
        )
        info += f"加载器: {', '.join(loaders)}\n"

        # 如果有更新日志，添加预览
        changelog = version.get("changelog", "")
        if changelog:
            preview = changelog[:100].replace("\n", " ")
            info += (
                f"更新日志: {preview}..."
                if len(changelog) > 100
                else f"更新日志: {changelog}"
            )

        return info

    def generate_mods_toml_dependency(
        self,
        project_id: str,
        mandatory: bool = True,
        version_range: str = "",
        ordering: str = "NONE",
        side: str = "BOTH",
        game_version: Optional[str] = None,
        loader: str = "forge",
        mod_version: Optional[str] = None,
    ) -> str:
        """
        生成 mods.toml 依赖配置

        Args:
            project_id: MOD 项目 ID 或 slug
            mandatory: 是否为必需依赖
            version_range: 版本范围 (如 "[1.0,2.0)")
            ordering: 加载顺序 (NONE, BEFORE, AFTER)
            side: 运行侧 (CLIENT, SERVER, BOTH)
            game_version: Minecraft 版本
            loader: 模组加载器类型 (forge, fabric, neoforge)

        Returns:
            mods.toml 依赖配置代码
        """
        project = self.api.get_project(project_id)
        if not project:
            return f"# 错误: 无法获取项目 {project_id} 的信息"

        versions = self.api.get_project_versions(project_id, game_version, loader)
        if not versions:
            version_range = version_range or "[0,)"
        else:
            latest_version = versions[0]["version_number"]
            if not version_range:
                version_range = f"[{latest_version},)"

        toml_code = f"""# {project["title"]}
# 描述: {project["description"]}
[[dependencies.your_mod_id]]
    modId = "{project["slug"]}"
    mandatory = {str(mandatory).lower()}
    versionRange = "{version_range}"
    ordering = "{ordering}"
    side = "{side}"
"""
        return toml_code

    def generate_fabric_mod_json_dependency(
        self,
        project_id: str,
        mandatory: bool = True,
        version_range: str = "",
        game_version: Optional[str] = None,
        loader: str = "fabric",
        mod_version: Optional[str] = None,
    ) -> str:
        """
        生成 fabric.mod.json 依赖配置

        Args:
            project_id: MOD 项目 ID 或 slug
            mandatory: 是否为必需依赖
            version_range: 版本范围 (如 "*" 或 ">=1.0.0")
            game_version: Minecraft 版本
            loader: 模组加载器类型 (应为 fabric)

        Returns:
            fabric.mod.json 依赖配置代码
        """
        project = self.api.get_project(project_id)
        if not project:
            return f"// 错误: 无法获取项目 {project_id} 的信息"

        versions = self.api.get_project_versions(project_id, game_version, loader)
        if not versions:
            version_range = version_range or "*"
            selected_version_number = mod_version or "未知"
        else:
            # 选择版本
            if mod_version:
                selected_version = None
                for v in versions:
                    if v.get("version_number") == mod_version:
                        selected_version = v
                        break
                if selected_version:
                    selected_version_number = selected_version["version_number"]
                else:
                    selected_version_number = versions[0]["version_number"]
                    print(
                        f"警告: 未找到版本 {mod_version}，使用最新版本 {selected_version_number}"
                    )
            else:
                selected_version_number = versions[0]["version_number"]

            if not version_range:
                version_range = f">={selected_version_number}"

        # Fabric 使用不同的版本范围格式
        # 将语义化版本转换为 Fabric 格式
        if version_range.startswith("[") or version_range.startswith("("):
            # 如果是 Maven 版本范围格式，转换为 Fabric 格式
            version_range = (
                version_range.replace("[", "")
                .replace("]", "")
                .replace("(", "")
                .replace(")", "")
            )
            if "," in version_range:
                parts = version_range.split(",")
                if len(parts) == 2:
                    min_ver = parts[0].strip()
                    max_ver = parts[1].strip()
                    if min_ver and max_ver:
                        version_range = f">={min_ver} <{max_ver}"
                    elif min_ver:
                        version_range = f">={min_ver}"
                    else:
                        version_range = f"<{max_ver}"

        json_code = f"""// {project["title"]}
// 描述: {project["description"]}
// MOD 版本: {selected_version_number}
// 在 fabric.mod.json 的 "depends" 或 "recommends" 字段中添加:
{{
    "depends": {{
        "{project["slug"]}": "{version_range}"
    }}
}}
// 或者如果是可选依赖:
{{
    "recommends": {{
        "{project["slug"]}": "{version_range}"
    }}
}}
"""
        return json_code

    def generate_full_dependency_info(
        self,
        project_id: str,
        game_version: Optional[str] = None,
        loader: str = "forge",
        config_mode: str = "full",
        dependency_type: str = "implementation",
        mod_version: Optional[str] = None,
    ) -> str:
        """
        生成完整的依赖信息（支持多种配置模式）

        Args:
            project_id: MOD 项目 ID 或 slug
            game_version: Minecraft 版本
            loader: 模组加载器类型 (forge, fabric, neoforge)
            config_mode: 配置模式 (full, gradle_only, config_only, fabric_json, minimal)
            dependency_type: Gradle 依赖类型 (implementation, compileOnly, runtimeOnly, api)
            mod_version: MOD 版本号（如果为 None 则使用最新版本）

        Returns:
            完整的依赖配置代码
        """
        project = self.api.get_project(project_id)
        if not project:
            return f"错误: 无法获取项目 {project_id} 的信息"

        # 获取版本信息
        versions = self.api.get_project_versions(project_id, game_version, loader)
        if versions:
            if mod_version:
                selected_version = None
                for v in versions:
                    if v.get("version_number") == mod_version:
                        selected_version = v
                        break
                if selected_version:
                    selected_version_number = selected_version["version_number"]
                else:
                    selected_version_number = versions[0]["version_number"]
            else:
                selected_version_number = versions[0]["version_number"]
        else:
            selected_version_number = mod_version or "未知"

        # 基本信息
        info_section = f"""
{"=" * 80}
MOD 信息: {project["title"]}
{"=" * 80}
项目 ID: {project["id"]}
Slug: {project["slug"]}
描述: {project["description"]}
客户端: {project["client_side"]}
服务端: {project["server_side"]}
项目页面: https://modrinth.com/mod/{project["slug"]}
游戏版本: {game_version or "任意"}
加载器: {loader}
MOD 版本: {selected_version_number}
依赖类型: {dependency_type}
配置模式: {config_mode}
"""

        # 根据配置模式生成不同的内容
        if config_mode == "minimal":
            # 最小模式：只生成 Gradle 依赖代码（不含注释和仓库配置）
            if not versions:
                return f"错误: 项目 {project['title']} 没有可用版本"

            selected_version = None
            if mod_version:
                for v in versions:
                    if v.get("version_number") == mod_version:
                        selected_version = v
                        break
            if not selected_version:
                selected_version = versions[0]

            if loader.lower() == "forge":
                if dependency_type in ["implementation", "api"]:
                    return f'{dependency_type} fg.deobf("maven.modrinth:{project["slug"]}:{selected_version["version_number"]}")'
                else:
                    return f'{dependency_type} "maven.modrinth:{project["slug"]}:{selected_version["version_number"]}"'
            else:
                return f'{dependency_type} "maven.modrinth:{project["slug"]}:{selected_version["version_number"]}"'

        elif config_mode == "gradle_only":
            # 仅 Gradle 模式
            return (
                info_section
                + f"""
{"=" * 80}
build.gradle 依赖配置:
{"=" * 80}
{self.generate_gradle_dependency(project_id, game_version=game_version, loader=loader, dependency_type=dependency_type, mod_version=mod_version)}
"""
            )

        elif config_mode == "config_only":
            # 仅配置文件模式
            if loader.lower() == "fabric":
                config_section = f"""
{"=" * 80}
fabric.mod.json 依赖配置:
{"=" * 80}
{self.generate_fabric_mod_json_dependency(project_id, game_version=game_version, loader=loader, mod_version=mod_version)}
"""
            else:
                config_section = f"""
{"=" * 80}
mods.toml 依赖配置:
{"=" * 80}
{self.generate_mods_toml_dependency(project_id, game_version=game_version, loader=loader, mod_version=mod_version)}
"""
            return info_section + config_section

        elif config_mode == "fabric_json":
            # Fabric JSON 模式
            return (
                info_section
                + f"""
{"=" * 80}
fabric.mod.json 依赖配置:
{"=" * 80}
{self.generate_fabric_mod_json_dependency(project_id, game_version=game_version, loader=loader, mod_version=mod_version)}
"""
            )

        else:
            # 完整模式（默认）：包含所有配置
            result = (
                info_section
                + f"""
{"=" * 80}
build.gradle 依赖配置:
{"=" * 80}
{self.generate_gradle_dependency(project_id, game_version=game_version, loader=loader, dependency_type=dependency_type, mod_version=mod_version)}
"""
            )

            # 根据加载器类型添加相应的配置文件
            if loader.lower() == "fabric":
                result += f"""
{"=" * 80}
fabric.mod.json 依赖配置:
{"=" * 80}
{self.generate_fabric_mod_json_dependency(project_id, game_version=game_version, loader=loader, mod_version=mod_version)}
"""
            else:
                result += f"""
{"=" * 80}
mods.toml 依赖配置:
{"=" * 80}
{self.generate_mods_toml_dependency(project_id, game_version=game_version, loader=loader, mod_version=mod_version)}
"""
            return result
