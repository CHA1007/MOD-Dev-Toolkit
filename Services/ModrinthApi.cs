using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Web;
using MODDevToolkit.Models;

namespace MODDevToolkit.Services
{
    /// <summary>Modrinth API 客户端，GET 响应带文件缓存</summary>
    public class ModrinthApi : IModSource
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;

        private static readonly TimeSpan SearchCacheTtl = TimeSpan.FromMinutes(30);
        private static readonly TimeSpan VersionCacheTtl = TimeSpan.FromMinutes(15);

        public string Name => "Modrinth";

        private static readonly HashSet<string> KnownLoaders = new(StringComparer.OrdinalIgnoreCase)
        {
            "forge", "fabric", "neoforge", "quilt", "liteloader", "rift", "modloader"
        };

        public ModrinthApi()
        {
            _baseUrl = AppSettings.Current.ApiBaseUrl.TrimEnd('/');
            _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "MOD-Dev-Toolkit/2.0.0");
        }

        // ==================== 搜索 ====================

        public async Task<SearchResult> SearchProjectsAsync(
            string query, string? loader = null, string? gameVersion = null,
            int limit = 20, int offset = 0)
        {
            var facets = new List<List<string>> { new() { "project_type:mod" } };
            if (!string.IsNullOrEmpty(loader))
                facets.Add(new List<string> { $"categories:{loader}" });
            if (!string.IsNullOrEmpty(gameVersion))
                facets.Add(new List<string> { $"versions:{gameVersion}" });

            var queryParams = HttpUtility.ParseQueryString("");
            queryParams["query"] = query;
            queryParams["facets"] = JsonSerializer.Serialize(facets);
            queryParams["limit"] = limit.ToString();
            queryParams["offset"] = offset.ToString();

            var url = $"{_baseUrl}/search?{queryParams}";
            var response = await ApiCache.GetWithCacheAsync(_httpClient, url, SearchCacheTtl);

            using var doc = JsonDocument.Parse(response);
            var root = doc.RootElement;

            var result = new SearchResult
            {
                Total = root.TryGetProperty("total_hits", out var total) ? total.GetInt32() : 0
            };

            if (root.TryGetProperty("hits", out var hits))
            {
                foreach (var hit in hits.EnumerateArray())
                {
                    var mod = new ModInfo
                    {
                        SourceName = "Modrinth",
                        ProjectId = hit.GetProperty("project_id").GetString() ?? "",
                        Slug = hit.GetProperty("slug").GetString() ?? "",
                        Title = hit.GetProperty("title").GetString() ?? "",
                        Description = hit.TryGetProperty("description", out var desc) ? desc.GetString() ?? "" : "",
                        IconUrl = hit.TryGetProperty("icon_url", out var icon) ? icon.GetString() ?? "" : "",
                        Downloads = hit.TryGetProperty("downloads", out var dl) ? dl.GetInt64() : 0,
                        DateModified = hit.TryGetProperty("date_modified", out var dm) ? dm.GetString() ?? "" : ""
                    };

                    if (hit.TryGetProperty("categories", out var categories))
                    {
                        foreach (var cat in categories.EnumerateArray())
                        {
                            var catName = cat.GetString() ?? "";
                            mod.Categories.Add(catName);
                            mod.DisplayCategories.Add(ModCategories.Display(catName));
                        }
                    }

                    // 搜索接口的 versions 是版本 id 数组
                    if (hit.TryGetProperty("versions", out var versions))
                    {
                        foreach (var ver in versions.EnumerateArray())
                            mod.Versions.Add(ver.GetString() ?? "");
                    }

                    // 加载器：从 display_categories 中识别已知加载器名
                    if (hit.TryGetProperty("display_categories", out var displayCats))
                    {
                        foreach (var d in displayCats.EnumerateArray())
                        {
                            var name = d.GetString() ?? "";
                            if (KnownLoaders.Contains(name))
                                mod.Loaders.Add(name);
                        }
                    }

                    result.Hits.Add(mod);
                }
            }

            return result;
        }

        // ==================== 版本列表 ====================

        public async Task<List<ModVersion>> GetProjectVersionsAsync(
            string projectId, string? gameVersion = null, string? loader = null)
        {
            var queryParams = HttpUtility.ParseQueryString("");
            if (!string.IsNullOrEmpty(gameVersion))
                queryParams["game_versions"] = $"[\"{gameVersion}\"]";
            if (!string.IsNullOrEmpty(loader))
                queryParams["loaders"] = $"[\"{loader}\"]";

            var url = $"{_baseUrl}/project/{projectId}/version";
            if (queryParams.Count > 0)
                url += $"?{queryParams}";

            var response = await ApiCache.GetWithCacheAsync(_httpClient, url, VersionCacheTtl);
            var versions = JsonSerializer.Deserialize<List<ModVersion>>(response,
                new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower });

            return versions ?? new List<ModVersion>();
        }

        // ==================== 连接测试 ====================

        public async Task<int> TestConnectionAsync()
        {
            var sw = Stopwatch.StartNew();
            var response = await _httpClient.GetStringAsync($"{_baseUrl}/search?query=stone&limit=1");
            sw.Stop();
            using var doc = JsonDocument.Parse(response); // 校验返回的是合法 JSON
            return (int)sw.ElapsedMilliseconds;
        }

        // ==================== 配置片段 ====================

        public string VersionTagFor(ModVersion version) => version.VersionNumber;

        public string? ResolveLatestTag(IReadOnlyList<ModVersion> loadedVersions) => "LATEST";

        public string GradleRepositories() => @"repositories {
    maven {
        name = ""Modrinth""
        url = ""https://api.modrinth.com/maven""
    }
}";

        public string GradleDependency(ModInfo mod, string versionTag, string dependencyType)
            => $"{dependencyType} \"maven.modrinth:{mod.Slug}:{versionTag}\"";
    }
}
