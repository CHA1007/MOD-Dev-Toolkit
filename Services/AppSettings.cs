using System;
using System.IO;
using Newtonsoft.Json;

namespace MODDevToolkit.Services
{
    /// <summary>应用设置，持久化到 %APPDATA%/MODDevToolkit/settings.json</summary>
    public class AppSettings
    {
        public static AppSettings Current { get; private set; } = new();

        /// <summary>主题色（十六进制）</summary>
        public string AccentColorHex { get; set; } = DefaultAccentColorHex;

        /// <summary>MOD 搜索 API 端点</summary>
        public string ApiBaseUrl { get; set; } = DefaultApiBaseUrl;

        /// <summary>CurseForge API Key，在 console.curseforge.com 申请</summary>
        public string CurseForgeApiKey { get; set; } = "";

        public const string DefaultAccentColorHex = "#4CA6E8";
        public const string DefaultApiBaseUrl = "https://api.modrinth.com/v2";

        private static string SettingsDir => Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "MODDevToolkit");

        private static string SettingsPath => Path.Combine(SettingsDir, "settings.json");

        public static void Load()
        {
            try
            {
                if (File.Exists(SettingsPath))
                {
                    var json = File.ReadAllText(SettingsPath);
                    Current = JsonConvert.DeserializeObject<AppSettings>(json) ?? new AppSettings();
                }
                else
                {
                    Current = new AppSettings();
                }
            }
            catch
            {
                Current = new AppSettings();
            }
            Current.Sanitize();
        }

        public void Save()
        {
            try
            {
                Directory.CreateDirectory(SettingsDir);
                File.WriteAllText(SettingsPath,
                    JsonConvert.SerializeObject(this, Formatting.Indented));
            }
            catch
            {
                // 写入失败不致命
            }
        }

        private void Sanitize()
        {
            if (string.IsNullOrWhiteSpace(AccentColorHex))
                AccentColorHex = DefaultAccentColorHex;
            if (string.IsNullOrWhiteSpace(ApiBaseUrl))
                ApiBaseUrl = DefaultApiBaseUrl;
            CurseForgeApiKey ??= "";
        }
    }
}
