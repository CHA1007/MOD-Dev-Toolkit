#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from typing import List, Dict, Optional
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


class ModrinthAPI:
    """Modrinth API 客户端"""
    
    BASE_URL = "https://api.modrinth.com/v2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Auto-Depen-Generator/1.0)',
        })
    
    def search_projects(self, query: str, loader: str = "forge", limit: int = 10, offset: int = 0) -> Dict:
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
        
        # requests 库会自动处理 URL 编码，确保 UTF-8
        params = {
            'query': query,
            'facets': f'[["project_type:mod"],["categories:{loader}"]]',
            'limit': limit,
            'offset': offset
        }
        # 注意：Modrinth API 的 facets 参数需要 JSON 数组格式
        
        try:
            # 确保响应使用 UTF-8 编码
            response = self.session.get(url, params=params)
            response.encoding = 'utf-8'  # 显式设置响应编码
            response.raise_for_status()
            data = response.json()
            return {
                'hits': data.get('hits', []),
                'total': data.get('total_hits', 0),
                'offset': offset
            }
        except Exception as e:
            print(f"搜索出错: {e}")
            return {'hits': [], 'total': 0, 'offset': offset}
    
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
    
    def get_project_versions(self, project_id: str, game_version: Optional[str] = None, 
                           loader: str = "forge") -> List[Dict]:
        """
        获取项目的所有版本
        
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
            params['game_versions'] = f'["{game_version}"]'
        if loader:
            params['loaders'] = f'["{loader}"]'
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            versions = response.json()
            if not versions:
                print(f"警告: 项目 {project_id} 没有找到匹配的版本 (游戏版本: {game_version or '任意'}, 加载器: {loader})")
            return versions
        except requests.exceptions.HTTPError as e:
            print(f"获取版本列表出错 (HTTP {e.response.status_code}): {e}")
            if e.response.status_code == 404:
                print(f"提示: 项目 {project_id} 可能不存在或已被删除")
            return []
        except Exception as e:
            print(f"获取版本列表出错: {e}")
            return []


class ForgeDepGenerator:
    """Forge MOD 依赖代码生成器"""
    
    def __init__(self, api: ModrinthAPI):
        self.api = api
    
    def generate_gradle_dependency(self, project_id: str, version: str = "latest", 
                                  game_version: Optional[str] = None, loader: str = "forge",
                                  dependency_type: str = "implementation") -> str:
        """
        生成 build.gradle 依赖配置
        
        Args:
            project_id: MOD 项目 ID 或 slug
            version: 版本号或 "latest"
            game_version: Minecraft 版本
            loader: 模组加载器类型 (forge, fabric, neoforge)
            dependency_type: 依赖类型 (implementation, compileOnly, runtimeOnly, api)
        
        Returns:
            Gradle 依赖配置代码
        """
        project = self.api.get_project(project_id)
        if not project:
            return f"// 错误: 无法获取项目 {project_id} 的信息"
        
        versions = self.api.get_project_versions(project_id, game_version, loader)
        if not versions:
            return f"// 错误: 项目 {project['title']} 没有可用版本（游戏版本: {game_version or '任意'}, 加载器: {loader}）"
        
        # 获取最新版本
        latest_version = versions[0]
        
        # 验证依赖类型
        valid_types = ["implementation", "compileOnly", "runtimeOnly", "api"]
        if dependency_type not in valid_types:
            dependency_type = "implementation"
        
        # 根据加载器类型选择不同的依赖格式
        if loader.lower() == "neoforge":
            # NeoForge 使用标准的依赖格式
            dependency_line = f'    {dependency_type} "maven.modrinth:{project["slug"]}:{latest_version["version_number"]}"'
        elif loader.lower() == "fabric":
            # Fabric 也使用标准的依赖格式
            dependency_line = f'    {dependency_type} "maven.modrinth:{project["slug"]}:{latest_version["version_number"]}"'
        else:
            # Forge 使用 fg.deobf 格式（仅对 implementation 和 api 类型）
            if dependency_type in ["implementation", "api"]:
                dependency_line = f'    {dependency_type} fg.deobf("maven.modrinth:{project["slug"]}:{latest_version["version_number"]}")'
            else:
                # compileOnly 和 runtimeOnly 不使用 fg.deobf
                dependency_line = f'    {dependency_type} "maven.modrinth:{project["slug"]}:{latest_version["version_number"]}"'
        
        # 构建 Gradle 依赖代码
        gradle_code = f"""// {project['title']}
// 描述: {project['description']}
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
    
    def generate_mods_toml_dependency(self, project_id: str, mandatory: bool = True,
                                     version_range: str = "", ordering: str = "NONE",
                                     side: str = "BOTH", game_version: Optional[str] = None,
                                     loader: str = "forge") -> str:
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
            latest_version = versions[0]['version_number']
            if not version_range:
                version_range = f"[{latest_version},)"
        
        toml_code = f"""# {project['title']}
# 描述: {project['description']}
[[dependencies.your_mod_id]]
    modId = "{project['slug']}"
    mandatory = {str(mandatory).lower()}
    versionRange = "{version_range}"
    ordering = "{ordering}"
    side = "{side}"
"""
        return toml_code
    
    def generate_fabric_mod_json_dependency(self, project_id: str, mandatory: bool = True,
                                          version_range: str = "", game_version: Optional[str] = None,
                                          loader: str = "fabric") -> str:
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
        else:
            latest_version = versions[0]['version_number']
            if not version_range:
                version_range = f">={latest_version}"
        
        # Fabric 使用不同的版本范围格式
        # 将语义化版本转换为 Fabric 格式
        if version_range.startswith("[") or version_range.startswith("("):
            # 如果是 Maven 版本范围格式，转换为 Fabric 格式
            version_range = version_range.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
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
        
        json_code = f"""// {project['title']}
// 描述: {project['description']}
// 在 fabric.mod.json 的 "depends" 或 "recommends" 字段中添加:
{{
    "depends": {{
        "{project['slug']}": "{version_range}"
    }}
}}
// 或者如果是可选依赖:
{{
    "recommends": {{
        "{project['slug']}": "{version_range}"
    }}
}}
"""
        return json_code
    
    def generate_full_dependency_info(self, project_id: str, game_version: Optional[str] = None, 
                                     loader: str = "forge", config_mode: str = "full",
                                     dependency_type: str = "implementation") -> str:
        """
        生成完整的依赖信息（支持多种配置模式）
        
        Args:
            project_id: MOD 项目 ID 或 slug
            game_version: Minecraft 版本
            loader: 模组加载器类型 (forge, fabric, neoforge)
            config_mode: 配置模式 (full, gradle_only, config_only, fabric_json, minimal)
            dependency_type: Gradle 依赖类型 (implementation, compileOnly, runtimeOnly, api)
        
        Returns:
            完整的依赖配置代码
        """
        project = self.api.get_project(project_id)
        if not project:
            return f"错误: 无法获取项目 {project_id} 的信息"
        
        # 基本信息
        info_section = f"""
{'='*80}
MOD 信息: {project['title']}
{'='*80}
项目 ID: {project['id']}
Slug: {project['slug']}
描述: {project['description']}
客户端: {project['client_side']}
服务端: {project['server_side']}
项目页面: https://modrinth.com/mod/{project['slug']}
游戏版本: {game_version or '任意'}
加载器: {loader}
依赖类型: {dependency_type}
配置模式: {config_mode}
"""
        
        # 根据配置模式生成不同的内容
        if config_mode == "minimal":
            # 最小模式：只生成 Gradle 依赖代码（不含注释和仓库配置）
            versions = self.api.get_project_versions(project_id, game_version, loader)
            if not versions:
                return f"错误: 项目 {project['title']} 没有可用版本"
            latest_version = versions[0]
            
            if loader.lower() == "forge":
                if dependency_type in ["implementation", "api"]:
                    return f'{dependency_type} fg.deobf("maven.modrinth:{project["slug"]}:{latest_version["version_number"]}")'
                else:
                    return f'{dependency_type} "maven.modrinth:{project["slug"]}:{latest_version["version_number"]}"'
            else:
                return f'{dependency_type} "maven.modrinth:{project["slug"]}:{latest_version["version_number"]}"'
        
        elif config_mode == "gradle_only":
            # 仅 Gradle 模式
            return info_section + f"""
{'='*80}
build.gradle 依赖配置:
{'='*80}
{self.generate_gradle_dependency(project_id, game_version=game_version, loader=loader, dependency_type=dependency_type)}
"""
        
        elif config_mode == "config_only":
            # 仅配置文件模式
            if loader.lower() == "fabric":
                config_section = f"""
{'='*80}
fabric.mod.json 依赖配置:
{'='*80}
{self.generate_fabric_mod_json_dependency(project_id, game_version=game_version, loader=loader)}
"""
            else:
                config_section = f"""
{'='*80}
mods.toml 依赖配置:
{'='*80}
{self.generate_mods_toml_dependency(project_id, game_version=game_version, loader=loader)}
"""
            return info_section + config_section
        
        elif config_mode == "fabric_json":
            # Fabric JSON 模式
            return info_section + f"""
{'='*80}
fabric.mod.json 依赖配置:
{'='*80}
{self.generate_fabric_mod_json_dependency(project_id, game_version=game_version, loader=loader)}
"""
        
        else:
            # 完整模式（默认）：包含所有配置
            result = info_section + f"""
{'='*80}
build.gradle 依赖配置:
{'='*80}
{self.generate_gradle_dependency(project_id, game_version=game_version, loader=loader, dependency_type=dependency_type)}
"""
            
            # 根据加载器类型添加相应的配置文件
            if loader.lower() == "fabric":
                result += f"""
{'='*80}
fabric.mod.json 依赖配置:
{'='*80}
{self.generate_fabric_mod_json_dependency(project_id, game_version=game_version, loader=loader)}
"""
            else:
                result += f"""
{'='*80}
mods.toml 依赖配置:
{'='*80}
{self.generate_mods_toml_dependency(project_id, game_version=game_version, loader=loader)}
"""
            return result


def interactive_mode():
    """交互式模式"""
    print("="*80)
    print("Modrinth API MOD 依赖生成器")
    print("="*80)
    
    api = ModrinthAPI()
    generator = ForgeDepGenerator(api)
    
    while True:
        print("\n" + "="*80)
        # 搜索 MOD
        query = input("\n请输入 MOD 搜索关键词 (输入 'q' 退出): ").strip()
        if query.lower() == 'q':
            print("感谢使用！")
            break
        
        if not query:
            print("搜索关键词不能为空！")
            continue
        
        loader = input("请输入加载器类型 (forge/fabric/neoforge，默认: forge): ").strip() or "forge"
        
        print(f"\n正在搜索 '{query}' (加载器: {loader})...")
        results = api.search_projects(query, loader=loader)
        
        if not results:
            print("没有找到相关 MOD，请尝试其他关键词")
            continue
        
        print(f"\n找到 {len(results)} 个结果:\n")
        for i, mod in enumerate(results, 1):
            print(f"{i}. {mod['title']}")
            print(f"   Slug: {mod['slug']}")
            print(f"   描述: {mod['description'][:100]}...")
            print(f"   下载量: {mod.get('downloads', 0)}")
            print()
        
        # 选择 MOD
        mod_choice = input("请选择要生成配置的 MOD (输入序号): ").strip()
        if not mod_choice.isdigit():
            print("无效的序号，跳过")
            continue
        
        idx = int(mod_choice) - 1
        if not (0 <= idx < len(results)):
            print("序号超出范围，跳过")
            continue
        
        selected_mod = results[idx]
        
        # 输入版本号和加载器
        game_version = input("请输入 Minecraft 版本 (如 1.21.1，按回车跳过): ").strip() or None
        use_loader = input(f"请输入加载器类型 (当前: {loader}，按回车使用当前值): ").strip() or loader
        
        # 选择配置模式
        print("\n配置模式:")
        print("  1. full - 完整模式（包含所有配置）")
        print("  2. gradle_only - 仅 Gradle 配置")
        print("  3. config_only - 仅配置文件（mods.toml 或 fabric.mod.json）")
        print("  4. fabric_json - 仅 Fabric JSON 配置")
        print("  5. minimal - 最小模式（仅依赖代码行）")
        config_mode_choice = input("请选择配置模式 (1-5，默认: 1): ").strip() or "1"
        config_mode_map = {"1": "full", "2": "gradle_only", "3": "config_only", "4": "fabric_json", "5": "minimal"}
        config_mode = config_mode_map.get(config_mode_choice, "full")
        
        # 选择依赖类型（仅对 Gradle 相关模式有效）
        dependency_type = "implementation"
        if config_mode in ["full", "gradle_only", "minimal"]:
            print("\nGradle 依赖类型:")
            print("  1. implementation - 实现依赖（默认）")
            print("  2. compileOnly - 仅编译时依赖")
            print("  3. runtimeOnly - 仅运行时依赖")
            print("  4. api - API 依赖")
            dep_type_choice = input("请选择依赖类型 (1-4，默认: 1): ").strip() or "1"
            dep_type_map = {"1": "implementation", "2": "compileOnly", "3": "runtimeOnly", "4": "api"}
            dependency_type = dep_type_map.get(dep_type_choice, "implementation")
        
        # 生成配置
        print("\n" + "="*80)
        print("生成依赖配置中...\n")
        config_output = generator.generate_full_dependency_info(
            selected_mod['slug'], 
            game_version, 
            use_loader,
            config_mode=config_mode,
            dependency_type=dependency_type
        )
        print(config_output)
        
        # 询问是否保存到文件
        save = input("\n是否保存到文件？(y/n): ").strip().lower()
        if save == 'y':
            filename = input("请输入文件名 (默认: dependency_output.txt): ").strip() or "dependency_output.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(config_output)
                print(f"已保存到 {filename}")
            except Exception as e:
                print(f"保存文件失败: {e}")


def main():
    """主函数"""
    import sys
    
    # 检查是否使用 GUI 模式
    if len(sys.argv) > 1 and sys.argv[1] in ['--gui', '-g']:
        try:
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"无法启动 GUI 模式: {e}")
            print("请确保 tkinter 已安装（通常 Python 自带）")
            print("启动命令行模式...\n")
            interactive_mode()
    else:
        # 默认使用命令行模式
        print("启动交互式模式...")
        print("提示: 使用 'python main.py --gui' 或 'python main.py -g' 启动 GUI 模式\n")
        interactive_mode()


if __name__ == '__main__':
    main()
