using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using MODDevToolkit.Models;
using MODDevToolkit.Services;

namespace MODDevToolkit.Pages
{
    public partial class HomePage : Page
    {
        // 与当前列表对应的源，打开配置窗口时使用
        private IModSource _lastSource = new ModrinthApi();

        public HomePage()
        {
            InitializeComponent();
        }

        private IModSource CurrentSource()
            => SourceCombo.SelectedIndex == 1 ? new CurseForgeApi() : new ModrinthApi();

        private void SearchBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter)
            {
                _ = SearchAsync();
            }
        }

        private async void SearchButton_Click(object sender, RoutedEventArgs e)
            => await SearchAsync();

        private async System.Threading.Tasks.Task SearchAsync()
        {
            var query = SearchBox.Text.Trim();
            if (string.IsNullOrEmpty(query))
            {
                MessageBox.Show("请输入搜索关键词", "提示",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var source = CurrentSource();
            // CurseForge 未配置密钥时不发请求，直接提示
            if (source is CurseForgeApi
                && string.IsNullOrWhiteSpace(AppSettings.Current.CurseForgeApiKey))
            {
                MessageBox.Show("请先在 设置 → 网络 中填写 CurseForge API Key\n（申请地址：console.curseforge.com）",
                    "提示", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            LoadingBar.Visibility = Visibility.Visible;
            ModList.ItemsSource = null;
            ModList.Visibility = Visibility.Collapsed;
            EmptyHint.Visibility = Visibility.Collapsed;

            try
            {
                string? loader = null;
                if (LoaderCombo.SelectedIndex > 0 && LoaderCombo.SelectedItem is ComboBoxItem item)
                {
                    loader = item.Content.ToString()?.ToLower();
                }

                string? gameVersion = null;
                var versionText = GameVersionCombo.Text?.Trim() ?? "";
                if (versionText.Length > 0 && !versionText.StartsWith("全部"))
                {
                    gameVersion = versionText;
                }

                var result = await source.SearchProjectsAsync(query, loader, gameVersion);
                _lastSource = source;

                ModList.ItemsSource = result.Hits;
                ResultCountText.Text = $"搜索结果（{result.Total} 个匹配）";

                if (result.Hits.Count > 0)
                {
                    ModList.Visibility = Visibility.Visible;
                    EmptyHint.Visibility = Visibility.Collapsed;
                }
                else
                {
                    ModList.Visibility = Visibility.Collapsed;
                    EmptyHint.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                ResultCountText.Text = "搜索结果";
                EmptyHint.Visibility = Visibility.Visible;
                MessageBox.Show($"搜索失败: {ex.Message}", "错误",
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                LoadingBar.Visibility = Visibility.Collapsed;
            }
        }

        private void ResetButton_Click(object sender, RoutedEventArgs e)
        {
            SearchBox.Clear();
            SourceCombo.SelectedIndex = 0;
            LoaderCombo.SelectedIndex = 0;
            GameVersionCombo.SelectedIndex = 0;
            ModList.ItemsSource = null;
            ModList.Visibility = Visibility.Collapsed;
            EmptyHint.Visibility = Visibility.Visible;
            ResultCountText.Text = "搜索结果";
        }

        private void GenerateConfig_Click(object sender, RoutedEventArgs e)
        {
            if (sender is FrameworkElement { Tag: ModInfo mod })
            {
                var dialog = new Windows.ConfigGeneratorWindow(mod, _lastSource)
                {
                    Owner = Application.Current.MainWindow
                };
                dialog.ShowDialog();
            }
        }
    }
}
