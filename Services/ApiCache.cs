using System;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

namespace MODDevToolkit.Services
{
    /// <summary>API GET 响应文件缓存（按 URL 哈希）</summary>
    public static class ApiCache
    {
        public static string CacheDir => Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "MODDevToolkit", "cache");

        public static string CachePathFor(string url)
        {
            var hash = Convert.ToHexString(SHA1.HashData(Encoding.UTF8.GetBytes(url)));
            return Path.Combine(CacheDir, hash + ".json");
        }

        public static async Task<string> GetWithCacheAsync(HttpClient http, string url, TimeSpan ttl)
        {
            try
            {
                var path = CachePathFor(url);
                if (File.Exists(path) && DateTime.UtcNow - File.GetLastWriteTimeUtc(path) < ttl)
                {
                    return await File.ReadAllTextAsync(path);
                }
            }
            catch
            {
                // 缓存读取失败，走网络
            }

            var response = await http.GetStringAsync(url);

            try
            {
                Directory.CreateDirectory(CacheDir);
                await File.WriteAllTextAsync(CachePathFor(url), response);
            }
            catch
            {
                // 缓存写入失败不影响结果
            }

            return response;
        }

        /// <summary>统计缓存占用</summary>
        public static (int Files, long Bytes) GetCacheInfo()
        {
            try
            {
                if (!Directory.Exists(CacheDir)) return (0, 0);
                var files = Directory.GetFiles(CacheDir);
                return (files.Length, files.Sum(f => new FileInfo(f).Length));
            }
            catch
            {
                return (0, 0);
            }
        }

        /// <summary>清空缓存，返回清理前的文件数与占用</summary>
        public static (int Files, long Bytes) ClearCache()
        {
            try
            {
                if (!Directory.Exists(CacheDir)) return (0, 0);
                var files = Directory.GetFiles(CacheDir);
                var info = (files.Length, files.Sum(f => new FileInfo(f).Length));
                foreach (var f in files)
                {
                    try { File.Delete(f); } catch { /* 忽略单个文件删除失败 */ }
                }
                return info;
            }
            catch
            {
                return (0, 0);
            }
        }
    }
}
