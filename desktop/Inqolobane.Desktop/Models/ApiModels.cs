using System.Text.Json.Serialization;

namespace Inqolobane.Desktop.Models;

public sealed class ApiList<T>
{
    [JsonPropertyName("items")]
    public List<T> Items { get; init; } = [];

    [JsonPropertyName("total")]
    public int Total { get; init; }
}

public sealed class CaseRecord
{
    [JsonPropertyName("complaint_ref")]
    public string ComplaintRef { get; init; } = "";

    [JsonPropertyName("customer_ref")]
    public string CustomerRef { get; init; } = "";

    [JsonPropertyName("account_ref")]
    public string? AccountRef { get; init; }

    [JsonPropertyName("product_type")]
    public string? ProductType { get; init; }

    [JsonPropertyName("category")]
    public string Category { get; init; } = "";

    [JsonPropertyName("subcategory")]
    public string? Subcategory { get; init; }

    [JsonPropertyName("priority")]
    public string Priority { get; init; } = "";

    [JsonPropertyName("status")]
    public string Status { get; init; } = "";

    [JsonPropertyName("allegation_status")]
    public string AllegationStatus { get; init; } = "";

    [JsonPropertyName("customer_summary")]
    public string CustomerSummary { get; init; } = "";

    [JsonPropertyName("opened_at")]
    public DateTimeOffset OpenedAt { get; init; }

    [JsonPropertyName("target_resolution_at")]
    public DateTimeOffset? TargetResolutionAt { get; init; }

    public string OpenedDisplay => OpenedAt.ToLocalTime().ToString("MMM d, yyyy");
}

public sealed class ProfileSnapshot
{
    [JsonPropertyName("customer_ref")]
    public string CustomerRef { get; init; } = "";

    [JsonPropertyName("system_name")]
    public string SystemName { get; init; } = "";

    [JsonPropertyName("field_name")]
    public string FieldName { get; init; } = "";

    [JsonPropertyName("field_value")]
    public string? FieldValue { get; init; }

    [JsonPropertyName("source_version")]
    public string? SourceVersion { get; init; }

    [JsonPropertyName("last_synced_at")]
    public DateTimeOffset? LastSyncedAt { get; init; }

    [JsonPropertyName("sync_status")]
    public string SyncStatus { get; init; } = "";

    [JsonPropertyName("observed_at")]
    public DateTimeOffset ObservedAt { get; init; }
}

public sealed class SourceDocument
{
    [JsonPropertyName("document_ref")]
    public string DocumentRef { get; init; } = "";

    [JsonPropertyName("filename")]
    public string Filename { get; init; } = "";

    [JsonPropertyName("title")]
    public string Title { get; init; } = "";

    [JsonPropertyName("related_refs")]
    public List<string> RelatedRefs { get; init; } = [];

    [JsonPropertyName("content")]
    public string Content { get; init; } = "";
}

public sealed class ReadinessResponse
{
    [JsonPropertyName("status")]
    public string Status { get; init; } = "";

    [JsonPropertyName("database")]
    public string Database { get; init; } = "";
}