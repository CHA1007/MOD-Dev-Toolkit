using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using MODDevToolkit.Models;
using MODDevToolkit.Services;

namespace MODDevToolkit.Windows
{
    public partial class ConfigGeneratorWindow : Wpf.Ui.Controls.FluentWindow
    {
        private readonly ModInfo _mod;
        private readonly IModSource _source;
        private readonly List<ModVersion> _loadedVersions = new();

        public ConfigGeneratorWindow(ModInfo mod, IModSource source)
        {
            InitializeComponent();
            _mod = mod;
            _source = source;

            ModTitle.Text = mod.Title;
            ModDescription.Text = mod.Description;

            LoadVersions();
        }

        private async void LoadVersions()
        {
            try
            {
                var versions = await _source.GetProjectVersionsAsync(_mod.ProjectId);
                _loadedVersions.Clear();
                _loadedVersions.AddRange(versions);

                ModVersionCombo.Items.Clear();
                ModVersionCombo.Items.Add(new ComboBoxItem
                {
                    Content = "最新版本",
                    Tag = "LATEST"
                });

                foreach (var version in versions.Take(20))
                {
                    var gameInfo = version.GameVersions.Count > 0
                        ? $" — {string.Join(", ", version.GameVersions.Take(3))}"
                        : "";
                    ModVersionCombo.Items.Add(new ComboBoxItem
                    {
                        Content = $"{version.VersionNumber}{gameInfo}",
                        Tag = _source.VersionTagFor(version)
                    });
                }

                ModVersionCombo.SelectedIndex = 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"加载版本失败: {ex.Message}");
            }
        }

        private void GenerateButton_Click(object sender, RoutedEventArgs e)
        {
            var configMode = ConfigModeCombo.SelectedIndex;
            var dependencyType = ((ComboBoxItem)DependencyTypeCombo.SelectedItem).Content.ToString() ?? "implementation";
            var versionItem = ModVersionCombo.SelectedItem as ComboBoxItem;
            var versionTag = versionItem?.Tag as string ?? "LATEST";

            if (versionTag == "LATEST")
            {
                var resolved = _source.ResolveLatestTag(_loadedVersions);
                if (resolved == null)
                {
                    MessageBox.Show("未能解析最新版本，请稍后重试", "提示",
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }
                versionTag = resolved;
            }

            ConfigResult.Text = GenerateConfig(configMode, dependencyType, versionTag);
        }

        private string GenerateConfig(int mode, string dependencyType, string versionTag)
        {
            switch (mode)
            {
                case 0: // 完整
                    return $@"// {_mod.Slug}
// 版本: {versionTag}

{_source.GradleRepositories()}

dependencies {{
    {_source.GradleDependency(_mod, versionTag, dependencyType)}
}}";

                case 1: // 仅 Gradle
                    return $@"dependencies {{
    {_source.GradleDependency(_mod, versionTag, dependencyType)}
}}";

                case 2: // 仅配置文件
                    // 两个源都无法从 API 得到真实 modId，用展示版本号与 slug 占位
                    var displayVersion = _loadedVersions
                        .FirstOrDefault(v => _source.VersionTagFor(v) == versionTag)?.VersionNumber ?? versionTag;
                    return $@"// mods.toml（modId 按实际情况调整）
[[dependencies.{_mod.Slug}]]
    modId = ""{_mod.Slug}""
    mandatory = true
    versionRange = ""[{displayVersion},)""
    ordering = ""NONE""
    side = ""BOTH""";

                case 3: // 最小
                    return _source.GradleDependency(_mod, versionTag, dependencyType);

                default:
                    return "";
            }
        }

        private void CopyButton_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(ConfigResult.Text))
            {
                Clipboard.SetText(ConfigResult.Text);
                MessageBox.Show("已复制到剪贴板", "成功",
                    MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(ConfigResult.Text))
            {
                MessageBox.Show("请先生成配置", "提示",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var dialog = new SaveFileDialog
            {
                FileName = $"{_mod.Slug}-dependency.txt",
                Filter = "文本文件 (*.txt)|*.txt|Gradle 文件 (*.gradle)|*.gradle|所有文件 (*.*)|*.*"
            };

            if (dialog.ShowDialog() == true)
            {
                File.WriteAllText(dialog.FileName, ConfigResult.Text);
                MessageBox.Show($"已保存到 {dialog.FileName}", "成功",
                    MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }

        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }
    }
}
