using System;
using System.Windows;
using System.Windows.Media;
using Wpf.Ui.Appearance;

namespace MODDevToolkit.Services
{
    /// <summary>主题色（Accent）切换</summary>
    public static class ThemeService
    {
        public static void ApplyAccent(string hex)
        {
            try
            {
                if (ColorConverter.ConvertFromString(hex) is Color color)
                {
                    ApplicationAccentColorManager.Apply(color);
                }
            }
            catch
            {
                // 非法颜色值时保持当前主题色
            }
        }

        /// <summary>重建主窗口使新主题色立即生效（WPF-UI 模板以 StaticResource 捕获画刷，改色后不会重读）</summary>
        public static void RefreshMainWindow(Type? stayOnPage = null)
        {
            if (Application.Current.MainWindow is MainWindow old)
            {
                var fresh = new MainWindow(stayOnPage)
                {
                    // XAML 默认 CenterScreen 会在 Show 时覆盖 Left/Top，必须改为 Manual
                    WindowStartupLocation = WindowStartupLocation.Manual,
                    Left = old.Left,
                    Top = old.Top,
                    Width = old.Width,
                    Height = old.Height,
                    WindowState = old.WindowState
                };

                Application.Current.MainWindow = fresh;
                fresh.Show();
                old.Close();
            }
        }
    }
}
