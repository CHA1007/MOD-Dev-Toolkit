using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;
using MODDevToolkit.Models;

namespace MODDevToolkit.Services
{
    /// <summary>CurseForge Core API 客户端，需在设置中配置 API Key</summary>
    public class CurseForgeApi : IModSource
    {
        private const string BaseUrl = "https://api.curseforge.com/v1";
        private const int MinecraftGameId = 432;
        private const int ModsClassId = 6;

        private static readonly TimeSpan SearchCacheTtl = TimeSpan.FromMinutes(30);
        private static readonly TimeSpan VersionCacheTtl = TimeSpan.FromMinutes(15);

        public string Name => "CurseForge";

        // CF 加载器枚举值（modLoaderType）
        private static readonly Dictionary<string, int> LoaderTypes = new(StringComparer.OrdinalIgnoreCase)
        {
            ["forge"] = 1, ["fabric"] = 4, ["quilt"] = 5, ["neoforge"] = 6
        };

        private static readonly Dictionary<int, string> LoaderNames = new()
        {
            [1] = "forge", [4] = "fabric", [5] = "quilt", [6] = "neoforge"
        };

        private readonly HttpClient _httpClient;

        public CurseForgeApi()
        {
            _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "MOD-Dev-Toolkit/2.0.0");
            _httpClient.DefaultRequestHeaders.Add("x-api-key", AppSettings.Current.CurseForgeApiKey);
        }

        // ==================== 搜索 ====================

        public async Task<SearchResult> SearchProjectsAsync(
            string query, string? loader = null, string? gameVersion = null,
            int limit = 20, int offset = 0)
        {
            var queryParams = HttpUtility.ParseQueryString("");
            queryParams["gameId"] = MinecraftGameId.ToString();
            queryParams["classId"] = ModsClassId.ToString();
            queryParams["searchFilter"] = query;
            queryParams["pageSize"] = limit.ToString();
            queryParams["index"] = offset.ToString();
            queryParams["sortField"] = "2"; // 按热度排序
            queryParams["sortOrder"] = "desc";
            if (!string.IsNullOrEmpty(gameVersion))
                queryParams["gameVersion"] = gameVersion;
            // CF 要求 modLoaderType 与 gameVersion 同时提供，缺版本时不加加载器过滤
            if (!string.IsNullOrEmpty(loader) && !string.IsNullOrEmpty(gameVersion)
                && LoaderTypes.TryGetValue(loader, out var loaderType))
                queryParams["modLoaderType"] = loaderType.ToString();

            var url = $"{BaseUrl}/mods/search?{queryParams}";
            var response = await GetAsync(url, SearchCacheTtl);

            using var doc = JsonDocument.Parse(response);
            var root = doc.RootElement;

            var result = new SearchResult();
            if (root.TryGetProperty("pagination", out var pagination)
                && pagination.TryGetProperty("totalCount", out var totalCount))
                result.Total = totalCount.GetInt32();

            if (root.TryGetProperty("data", out var data))
            {
                foreach (var item in data.EnumerateArray())
                    result.Hits.Add(MapMod(item));
            }

            return result;
        }

        private static ModInfo MapMod(JsonElement item)
        {
            var mod = new ModInfo
            {
                SourceName = "CurseForge",
                ProjectId = item.TryGetProperty("id", out var id) ? id.ToString() : "",
                Slug = Str(item, "slug"),
                Title = Str(item, "name"),
                Description = Str(item, "summary"),
                IconUrl = LogoUrl(item),
                Downloads = item.TryGetProperty("downloadCount", out var dl)
                    && dl.ValueKind == JsonValueKind.Number ? (long)dl.GetDouble() : 0,
                DateModified = FirstString(item, "dateModified", "dateReleased")
            };

            if (item.TryGetProperty("categories", out var categories))
            {
                foreach (var cat in categories.EnumerateArray())
                {
                    var catName = Str(cat, "name");
                    if (catName.Length == 0) continue;
                    mod.Categories.Add(catName);
                    mod.DisplayCategories.Add(ModCategories.Display(catName));
                }
            }

            // 加载器：从 latestFilesIndexes 的 modLoader 枚举去重
            if (item.TryGetProperty("latestFilesIndexes", out var indexes))
            {
                foreach (var idx in indexes.EnumerateArray())
                {
                    if (idx.TryGetProperty("modLoader", out var ml)
                        && ml.ValueKind == JsonValueKind.Number
                        && LoaderNames.TryGetValue(ml.GetInt32(), out var loaderName)
                        && !mod.Loaders.Contains(loaderName))
                        mod.Loaders.Add(loaderName);
                }
            }

            return mod;
        }

        // ==================== 版本列表 ====================

        public async Task<List<ModVersion>> GetProjectVersionsAsync(
            string projectId, string? gameVersion = null, string? loader = null)
        {
            var queryParams = HttpUtility.ParseQueryString("");
            queryParams["pageSize"] = "50";
            if (!string.IsNullOrEmpty(gameVersion))
                queryParams["gameVersion"] = gameVersion;
            if (!string.IsNullOrEmpty(loader) && !string.IsNullOrEmpty(gameVersion)
                && LoaderTypes.TryGetValue(loader, out var loaderType))
                queryParams["modLoaderType"] = loaderType.ToString();

            var url = $"{BaseUrl}/mods/{projectId}/files?{queryParams}";
            var response = await GetAsync(url, VersionCacheTtl);

            var versions = new List<ModVersion>();
            using var doc = JsonDocument.Parse(response);
            if (!doc.RootElement.TryGetProperty("data", out var data))
                return versions;

            foreach (var file in data.EnumerateArray())
            {
                var version = new ModVersion
                {
                    VersionId = file.TryGetProperty("id", out var id) ? id.ToString() : "",
                    VersionNumber = Str(file, "displayName"),
                    DatePublished = Str(file, "fileDate")
                };
                if (version.VersionNumber.Length == 0)
                    version.VersionNumber = Str(file, "fileName");

                // CF 的 gameVersions 数组混有加载器名，分离到 Loaders
                if (file.TryGetProperty("gameVersions", out var gameVersions))
                {
                    foreach (var v in gameVersions.EnumerateArray())
                    {
                        var token = v.GetString() ?? "";
                        if (LoaderTypes.ContainsKey(token))
                        {
                            var loaderName = token.ToLowerInvariant();
                            if (!version.Loaders.Contains(loaderName))
                                version.Loaders.Add(loaderName);
                        }
                        else
                        {
                            version.GameVersions.Add(token);
                        }
                    }
                }
                versions.Add(version);
            }
            return versions;
        }

        // ==================== 连接测试 ====================

        public async Task<int> TestConnectionAsync()
        {
            var sw = Stopwatch.StartNew();
            var url = $"{BaseUrl}/mods/search?gameId={MinecraftGameId}&classId={ModsClassId}&searchFilter=stone&pageSize=1";
            var response = await GetAsync(url, TimeSpan.Zero); // TTL 为 0 强制走网络
            sw.Stop();
            using var doc = JsonDocument.Parse(response); // 校验返回的是合法 JSON
            return (int)sw.ElapsedMilliseconds;
        }

        private async Task<string> GetAsync(string url, TimeSpan ttl)
        {
            try
            {
                return await ApiCache.GetWithCacheAsync(_httpClient, url, ttl);
            }
            // 密钥缺失或无效时 CF 返回 403（个别情况 401）
            catch (HttpRequestException ex) when (ex.StatusCode is HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden)
            {
                throw new HttpRequestException("CurseForge API Key 无效或缺失，请到 设置 → 网络 检查密钥");
            }
        }

        // ==================== 配置片段 ====================

        public string VersionTagFor(ModVersion version) => version.VersionId;

        public string? ResolveLatestTag(IReadOnlyList<ModVersion> loadedVersions)
            => loadedVersions.Count > 0 ? loadedVersions[0].VersionId : null;

        public string GradleRepositories() => @"repositories {
    maven {
        name = ""CurseMaven""
        url = ""https://cursemaven.com""
        content {
            includeGroup ""curse.maven""
        }
    }
}";

        public string GradleDependency(ModInfo mod, string versionTag, string dependencyType)
            => $"{dependencyType} \"curse.maven:{Descriptor(mod.Slug)}-{mod.ProjectId}:{versionTag}\"";

        // cursemaven 描述符仅允许小写字母与数字
        private static string Descriptor(string slug)
            => Regex.Replace(slug.ToLowerInvariant(), "[^a-z0-9]", "-");

        // ==================== JSON 辅助 ====================

        // JSON null 时返回空串（GetString 对 null 会抛异常）
        private static string Str(JsonElement obj, string name)
            => obj.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.String
                ? v.GetString() ?? "" : "";

        private static string FirstString(JsonElement obj, params string[] names)
        {
            foreach (var name in names)
            {
                var value = Str(obj, name);
                if (value.Length > 0) return value;
            }
            return "";
        }

        private static string LogoUrl(JsonElement item)
        {
            if (!item.TryGetProperty("logo", out var logo) || logo.ValueKind != JsonValueKind.Object)
                return "";
            var thumbnail = Str(logo, "thumbnailUrl");
            return thumbnail.Length > 0 ? thumbnail : Str(logo, "url");
        }
    }
}
