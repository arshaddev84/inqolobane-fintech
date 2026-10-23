using System.Net.Http.Json;
using System.Text.Json;
using Inqolobane.Desktop.Models;

namespace Inqolobane.Desktop.Services;

public sealed class OperationsApiClient : IDisposable
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    private readonly HttpClient _httpClient;

    public OperationsApiClient()
    {
        var configuredUrl = Environment.GetEnvironmentVariable("INQOLOBANE_API_URL");
        var baseUrl = string.IsNullOrWhiteSpace(configuredUrl)
            ? "http://localhost:8000/api/v1/"
            : configuredUrl.TrimEnd('/') + "/";

        _httpClient = new HttpClient
        {
            BaseAddress = new Uri(baseUrl, UriKind.Absolute),
            Timeout = TimeSpan.FromSeconds(12)
        };
    }

    public Task<ReadinessResponse> GetReadinessAsync(CancellationToken cancellationToken = default) =>
        GetAsync<ReadinessResponse>("health/ready", cancellationToken);

    public Task<ApiList<CaseRecord>> GetCasesAsync(
        string search,
        string? status,
        CancellationToken cancellationToken = default)
    {
        var query = new List<string> { "limit=100" };
        if (!string.IsNullOrWhiteSpace(search))
            query.Add($"search={Uri.EscapeDataString(search.Trim())}");
        if (!string.IsNullOrWhiteSpace(status))
            query.Add($"status={Uri.EscapeDataString(status)}");

        return GetAsync<ApiList<CaseRecord>>($"cases?{string.Join('&', query)}", cancellationToken);
    }

    public Task<ApiList<ProfileSnapshot>> GetProfilesAsync(
        string search,
        string? syncStatus,
        CancellationToken cancellationToken = default)
    {
        var query = new List<string>();
        if (!string.IsNullOrWhiteSpace(search))
            query.Add($"search={Uri.EscapeDataString(search.Trim())}");
        if (!string.IsNullOrWhiteSpace(syncStatus))
            query.Add($"sync_status={Uri.EscapeDataString(syncStatus)}");

        var path = query.Count == 0 ? "profiles/snapshots" : $"profiles/snapshots?{string.Join('&', query)}";
        return GetAsync<ApiList<ProfileSnapshot>>(path, cancellationToken);
    }

    public Task<ApiList<SourceDocument>> GetDocumentsAsync(
        string search,
        CancellationToken cancellationToken = default)
    {
        var path = string.IsNullOrWhiteSpace(search)
            ? "documents"
            : $"documents?search={Uri.EscapeDataString(search.Trim())}";
        return GetAsync<ApiList<SourceDocument>>(path, cancellationToken);
    }

    private async Task<T> GetAsync<T>(string path, CancellationToken cancellationToken)
    {
        using var response = await _httpClient.GetAsync(path, cancellationToken);
        if (!response.IsSuccessStatusCode)
            throw new HttpRequestException($"API returned HTTP {(int)response.StatusCode}.");

        return await response.Content.ReadFromJsonAsync<T>(JsonOptions, cancellationToken)
            ?? throw new JsonException("The API returned an empty response.");
    }

    public void Dispose() => _httpClient.Dispose();
}