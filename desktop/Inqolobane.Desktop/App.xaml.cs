using Microsoft.UI.Xaml;
using Inqolobane.Desktop.Services;

namespace Inqolobane.Desktop;

public partial class App : Application
{
    private Window? _window;

    public App()
    {
        UnhandledException += (_, args) =>
            StartupDiagnostics.Write("Unhandled WinUI exception", args.Exception);
        AppDomain.CurrentDomain.UnhandledException += (_, args) =>
            StartupDiagnostics.Write("Unhandled application exception", args.ExceptionObject as Exception);
        try
        {
            StartupDiagnostics.Write("App InitializeComponent started");
            InitializeComponent();
            StartupDiagnostics.Write("App InitializeComponent completed");
        }
        catch (Exception exception)
        {
            StartupDiagnostics.Write("App InitializeComponent failed", exception);
            throw;
        }
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        StartupDiagnostics.Write("OnLaunched started");
        try
        {
            _window = new MainWindow();
            StartupDiagnostics.Write("MainWindow constructed");
            _window.Activate();
            StartupDiagnostics.Write("Window activation requested");
        }
        catch (Exception exception)
        {
            StartupDiagnostics.Write("Window startup failed", exception);
            throw;
        }
    }
}