using System;
using System.Diagnostics;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using MODDevToolkit.Services;

namespace MODDevToolkit.Pages
{
    public partial class SettingsPage : Page
    {
        public SettingsPage()
        {
            InitializeComponent();
            Loaded += SettingsPage_Loaded;
        }

        private void SettingsPage_Loaded(object sender, RoutedEventArgs e)
        {
            ApiEndpointBox.Text = AppSettings.Current.ApiBaseUrl;
            EndpointCurrent.Text = "当前端点：" + AppSettings.Current.ApiBaseUrl;
            ApiKeyBox.Password = AppSettings.Current.CurseForgeApiKey;
            UpdateSwatchSelection();
            UpdateCacheInfo();
        }

        // ---------- 主题颜色 ----------

        private void Swatch_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button { Tag: string hex })
            {
                ThemeService.ApplyAccent(hex);
                AppSettings.Current.AccentColorHex = hex;
                AppSettings.Current.Save();

                // 重建主窗口使新主题色立即生效
                ThemeService.RefreshMainWindow(typeof(SettingsPage));
            }
        }

        private void UpdateSwatchSelection()
        {
            var current = AppSettings.Current.AccentColorHex;
            foreach (var swatch in SwatchPanel.Children.OfType<Button>())
            {
                var selected = string.Equals(swatch.Tag as string, current,
                    StringComparison.OrdinalIgnoreCase);
                swatch.ApplyTemplate();
                if (swatch.Template.FindName("ring", swatch) is UIElement ring)
                    ring.Visibility = selected ? Visibility.Visible : Visibility.Collapsed;
                if (swatch.Template.FindName("check", swatch) is UIElement check)
                    check.Visibility = selected ? Visibility.Visible : Visibility.Collapsed;
            }
        }

        // ---------- Modrinth API 端点 ----------

        private async void TestEndpoint_Click(object sender, RoutedEventArgs e)
        {
            var url = ApiEndpointBox.Text.Trim().TrimEnd('/');
            if (!Uri.TryCreate(url, UriKind.Absolute, out var uri) ||
                (uri.Scheme != "http" && uri.Scheme != "https"))
            {
                ShowApiInfo("无效的 URL", "请输入以 http:// 或 https:// 开头的地址",
                    Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            // 先保存，后续请求走新端点
            AppSettings.Current.ApiBaseUrl = url;
            AppSettings.Current.Save();
            EndpointCurrent.Text = "当前端点：" + url;

            try
            {
                var api = new ModrinthApi();
                var latency = await api.TestConnectionAsync();
                ShowApiInfo("连接成功", $"端点可用，响应耗时 {latency} ms",
                    Wpf.Ui.Controls.InfoBarSeverity.Success);
            }
            catch (Exception ex)
            {
                ShowApiInfo("连接失败", ex.Message, Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void ResetEndpoint_Click(object sender, RoutedEventArgs e)
        {
            ApiEndpointBox.Text = AppSettings.DefaultApiBaseUrl;
            AppSettings.Current.ApiBaseUrl = AppSettings.DefaultApiBaseUrl;
            AppSettings.Current.Save();
            EndpointCurrent.Text = "当前端点：" + AppSettings.DefaultApiBaseUrl;
            ShowApiInfo("已恢复默认", AppSettings.DefaultApiBaseUrl,
                Wpf.Ui.Controls.InfoBarSeverity.Informational);
        }

        private void ShowApiInfo(string title, string message, Wpf.Ui.Controls.InfoBarSeverity severity)
        {
            ApiInfoBar.Title = title;
            ApiInfoBar.Message = message;
            ApiInfoBar.Severity = severity;
            ApiInfoBar.IsOpen = true;
        }

        // ---------- CurseForge 密钥 ----------

        private async void TestKey_Click(object sender, RoutedEventArgs e)
        {
            var key = ApiKeyBox.Password.Trim();
            if (key.Length == 0)
            {
                ShowKeyInfo("请先输入 Key", "申请地址：console.curseforge.com",
                    Wpf.Ui.Controls.InfoBarSeverity.Warning);
                return;
            }

            // 先保存，CurseForgeApi 构造时读取
            AppSettings.Current.CurseForgeApiKey = key;
            AppSettings.Current.Save();

            try
            {
                var latency = await new CurseForgeApi().TestConnectionAsync();
                ShowKeyInfo("验证成功", $"Key 可用，响应耗时 {latency} ms",
                    Wpf.Ui.Controls.InfoBarSeverity.Success);
            }
            catch (Exception ex)
            {
                ShowKeyInfo("验证失败", ex.Message, Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void ClearKey_Click(object sender, RoutedEventArgs e)
        {
            ApiKeyBox.Password = "";
            AppSettings.Current.CurseForgeApiKey = "";
            AppSettings.Current.Save();
            ShowKeyInfo("已清空", "CurseForge 搜索将不可用",
                Wpf.Ui.Controls.InfoBarSeverity.Informational);
        }

        private void OpenKeyPage_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // UseShellExecute 才能用默认浏览器打开链接
                Process.Start(new ProcessStartInfo("https://console.curseforge.com/#/api-keys/minecraft")
                {
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                ShowKeyInfo("无法打开浏览器", ex.Message, Wpf.Ui.Controls.InfoBarSeverity.Error);
            }
        }

        private void ShowKeyInfo(string title, string message, Wpf.Ui.Controls.InfoBarSeverity severity)
        {
            KeyInfoBar.Title = title;
            KeyInfoBar.Message = message;
            KeyInfoBar.Severity = severity;
            KeyInfoBar.IsOpen = true;
        }

        // ---------- 缓存 ----------

        private void UpdateCacheInfo()
        {
            var (files, bytes) = ApiCache.GetCacheInfo();
            CacheSizeText.Text = $"占用 {FormatSize(bytes)}（{files} 个文件）";
        }

        private void ClearCache_Click(object sender, RoutedEventArgs e)
        {
            var (files, bytes) = ApiCache.ClearCache();
            UpdateCacheInfo();
            CacheInfoBar.Title = "已清理";
            CacheInfoBar.Message = $"删除 {files} 个文件，释放 {FormatSize(bytes)}";
            CacheInfoBar.Severity = Wpf.Ui.Controls.InfoBarSeverity.Success;
            CacheInfoBar.IsOpen = true;
        }

        private static string FormatSize(long bytes)
        {
            if (bytes >= 1024 * 1024) return $"{bytes / 1024.0 / 1024.0:0.##} MB";
            if (bytes >= 1024) return $"{bytes / 1024.0:0.##} KB";
            return $"{bytes} B";
        }
    }
}
