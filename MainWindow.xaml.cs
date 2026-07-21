using System;
using MODDevToolkit.Pages;

namespace MODDevToolkit
{
    public partial class MainWindow : Wpf.Ui.Controls.FluentWindow
    {
        private readonly Type _initialPage;

        // StartupUri 经反射创建主窗口，必须保留真正的无参构造函数
        public MainWindow() : this(null) { }

        /// <param name="initialPage">启动页，默认首页（重建窗口时用于停留原页面）</param>
        public MainWindow(Type? initialPage)
        {
            _initialPage = initialPage ?? typeof(HomePage);
            InitializeComponent();
        }

        protected override void OnContentRendered(EventArgs e)
        {
            base.OnContentRendered(e);
            RootNavigation.Navigate(_initialPage);
        }
    }
}
