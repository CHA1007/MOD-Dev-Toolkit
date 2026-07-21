using System;
using System.Windows;
using System.Windows.Threading;
using MODDevToolkit.Services;

namespace MODDevToolkit
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            // 先加载设置并应用主题色，再显示窗口
            AppSettings.Load();
            ThemeService.ApplyAccent(AppSettings.Current.AccentColorHex);

            // 全局异常兜底，避免闪退
            DispatcherUnhandledException += App_DispatcherUnhandledException;

            base.OnStartup(e);
        }

        private void App_DispatcherUnhandledException(
            object sender, DispatcherUnhandledExceptionEventArgs e)
        {
            MessageBox.Show(
                "发生未处理的异常：\n\n" + e.Exception +
                "\n\n（如频繁出现，请带上以上内容反馈给开发者）",
                "MOD开发工具箱 — 出错了",
                MessageBoxButton.OK,
                MessageBoxImage.Error);

            // 启动期主窗口未加载则直接退出，避免僵尸进程
            e.Handled = true;
            if (MainWindow == null || !MainWindow.IsLoaded)
            {
                Shutdown();
            }
        }
    }
}
