using System;
using System.Collections.Generic;
using System.Globalization;
using System.Windows;

namespace MODDevToolkit.Models
{
    public class ModInfo
    {
        public string SourceName { get; set; } = "";
        public string ProjectId { get; set; } = "";
        public string Slug { get; set; } = "";
        public string Title { get; set; } = "";
        public string Description { get; set; } = "";
        public string IconUrl { get; set; } = "";
        public long Downloads { get; set; }
        public string ClientSide { get; set; } = "";
        public string ServerSide { get; set; } = "";
        public string DateModified { get; set; } = "";
        public List<string> Categories { get; set; } = new();
        public List<string> DisplayCategories { get; set; } = new();
        public List<string> Versions { get; set; } = new();
        public List<string> Loaders { get; set; } = new();

        // 显示用字段
        public string Tags => string.Join(" / ", DisplayCategories);
        public Visibility TagsVisibility => DisplayCategories.Count > 0 ? Visibility.Visible : Visibility.Collapsed;

        /// <summary>兼容信息：加载器列表（来自 Modrinth display_categories）</summary>
        public string CompatInfo => Loaders.Count > 0 ? string.Join(" / ", Loaders) : "";

        public Visibility CompatVisibility => Loaders.Count > 0 ? Visibility.Visible : Visibility.Collapsed;

        /// <summary>版本数（来自搜索结果的 versions 数组）</summary>
        public string VersionCountText => Versions.Count > 0 ? $"{Versions.Count} 个版本" : "";

        public Visibility VersionCountVisibility => Versions.Count > 0 ? Visibility.Visible : Visibility.Collapsed;

        public string UpdateTime
        {
            get
            {
                if (string.IsNullOrEmpty(DateModified))
                    return "";

                if (DateTime.TryParse(DateModified, null, DateTimeStyles.RoundtripKind, out var date))
                {
                    var span = DateTime.UtcNow - date.ToUniversalTime();
                    if (span.TotalMinutes < 1) return "刚刚";
                    if (span.TotalHours < 1) return $"{(int)span.TotalMinutes} 分钟前";
                    if (span.TotalDays < 1) return $"{(int)span.TotalHours} 小时前";
                    if (span.TotalDays < 30) return $"{(int)span.TotalDays} 天前";
                    if (span.TotalDays < 365) return $"{(int)(span.TotalDays / 30)} 个月前";
                    return $"{(int)(span.TotalDays / 365)} 年前";
                }
                return "";
            }
        }

        public string DownloadsText
        {
            get
            {
                if (Downloads >= 100_000_000)
                    return (Downloads / 100_000_000.0).ToString("0.##", CultureInfo.InvariantCulture) + " 亿";
                if (Downloads >= 10_000)
                    return (Downloads / 10_000.0).ToString("0.##", CultureInfo.InvariantCulture) + " 万";
                return Downloads.ToString("N0");
            }
        }
    }

    public class ModVersion
    {
        public string VersionId { get; set; } = "";
        public string VersionNumber { get; set; } = "";
        public List<string> GameVersions { get; set; } = new();
        public List<string> Loaders { get; set; } = new();
        public string DatePublished { get; set; } = "";
    }

    public class SearchResult
    {
        public List<ModInfo> Hits { get; set; } = new();
        public int Total { get; set; }
    }
}
