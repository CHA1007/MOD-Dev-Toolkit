using System.Collections.Generic;
using System.Threading.Tasks;
using MODDevToolkit.Models;

namespace MODDevToolkit.Services
{
    /// <summary>MOD 源抽象，Modrinth 与 CurseForge 共用</summary>
    public interface IModSource
    {
        string Name { get; }

        Task<SearchResult> SearchProjectsAsync(string query, string? loader = null,
            string? gameVersion = null, int limit = 20, int offset = 0);

        Task<List<ModVersion>> GetProjectVersionsAsync(string projectId,
            string? gameVersion = null, string? loader = null);

        /// <summary>轻量请求测试连通性，返回耗时（毫秒）</summary>
        Task<int> TestConnectionAsync();

        /// <summary>版本下拉项携带的标识（Modrinth 为版本号，CurseForge 为 fileId）</summary>
        string VersionTagFor(ModVersion version);

        /// <summary>解析「最新版本」对应的依赖标识，无法解析时返回 null</summary>
        string? ResolveLatestTag(IReadOnlyList<ModVersion> loadedVersions);

        /// <summary>完整 Gradle repositories 块</summary>
        string GradleRepositories();

        /// <summary>单行 Gradle 依赖</summary>
        string GradleDependency(ModInfo mod, string versionTag, string dependencyType);
    }
}
