namespace Inqolobane.Desktop.Services;

internal static class StartupDiagnostics
{
    private static readonly string LogPath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "Inqolobane",
        "startup.log");

    public static void Write(string message, Exception? exception = null)
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(LogPath)!);
            var detail = exception is null
                ? message
                : $"{message}{Environment.NewLine}{exception}";
            File.AppendAllText(LogPath, $"{DateTimeOffset.Now:O} {detail}{Environment.NewLine}");
        }
        catch
        {
        }
    }
}