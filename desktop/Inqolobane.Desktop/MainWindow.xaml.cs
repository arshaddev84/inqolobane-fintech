using Inqolobane.Desktop.Models;
using Inqolobane.Desktop.Services;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Windows.System;

namespace Inqolobane.Desktop;

public sealed partial class MainWindow : Window
{
    private readonly OperationsApiClient _apiClient = new();
    private CancellationTokenSource? _loadCancellation;
    private bool _initialized;

    public MainWindow()
    {
        StartupDiagnostics.Write("MainWindow InitializeComponent started");
        InitializeComponent();
        StartupDiagnostics.Write("MainWindow InitializeComponent completed");
        _initialized = true;
        Activated += OnWindowActivated;
        Closed += (_, _) =>
        {
            _loadCancellation?.Cancel();
            _apiClient.Dispose();
        };
    }

    private async void OnWindowActivated(object sender, WindowActivatedEventArgs args)
    {
        Activated -= OnWindowActivated;
        StartupDiagnostics.Write("Window activated; initial API load started");
        await LoadDataAsync();
        StartupDiagnostics.Write("Initial API load completed");
    }

    private async Task LoadDataAsync()
    {
        _loadCancellation?.Cancel();
        var cancellation = new CancellationTokenSource();
        _loadCancellation = cancellation;
        var token = cancellation.Token;

        RefreshButton.IsEnabled = false;
        ApiStatusText.Text = "Loading live records…";
        ErrorBanner.Visibility = Visibility.Collapsed;

        var search = SearchBox.Text.Trim();
        var caseStatus = GetSelectedTag(CaseStatusFilter);
        var profileStatus = GetSelectedTag(ProfileStatusFilter);

        var readinessTask = TryLoadAsync(() => _apiClient.GetReadinessAsync(token), token);
        var casesTask = TryLoadAsync(() => _apiClient.GetCasesAsync(search, caseStatus, token), token);
        var profilesTask = TryLoadAsync(() => _apiClient.GetProfilesAsync(search, profileStatus, token), token);
        var documentsTask = TryLoadAsync(() => _apiClient.GetDocumentsAsync(search, token), token);

        try
        {
            await Task.WhenAll(readinessTask, casesTask, profilesTask, documentsTask);
            if (token.IsCancellationRequested)
                return;

            var readiness = await readinessTask;
            var cases = await casesTask;
            var profiles = await profilesTask;
            var documents = await documentsTask;
            var errors = new List<string>();

            if (readiness.Value is not null && readiness.Value.Database.Equals("ok", StringComparison.OrdinalIgnoreCase))
            {
                ApiStatusText.Text = "API and database connected";
                DatabaseMetric.Text = "Connected";
                DatabaseMetric.Foreground = (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources["AccentBrush"];
                ConnectionDot.Fill = (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources["AccentBrush"];
            }
            else
            {
                ApiStatusText.Text = "API or database unavailable";
                DatabaseMetric.Text = "Offline";
                DatabaseMetric.Foreground = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.OrangeRed);
                ConnectionDot.Fill = new Microsoft.UI.Xaml.Media.SolidColorBrush(Microsoft.UI.Colors.OrangeRed);
                errors.Add($"Database readiness: {readiness.Error ?? "The readiness endpoint did not report a healthy database."}");
            }

            ApplyCases(cases.Value, cases.Error, errors);
            ApplyProfiles(profiles.Value, profiles.Error, errors);
            ApplyDocuments(documents.Value, documents.Error, errors);

            if (errors.Count > 0)
            {
                ErrorText.Text = string.Join("  ·  ", errors);
                ErrorBanner.Visibility = Visibility.Visible;
            }
        }
        finally
        {
            if (_loadCancellation == cancellation)
            {
                _loadCancellation = null;
                RefreshButton.IsEnabled = true;
            }
            cancellation.Dispose();
        }
    }

    private async Task<(T? Value, string? Error)> TryLoadAsync<T>(
        Func<Task<T>> load,
        CancellationToken cancellationToken)
    {
        try
        {
            return (await load(), null);
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
            return (default, null);
        }
        catch (Exception error)
        {
            return (default, error.Message);
        }
    }

    private void ApplyCases(ApiList<CaseRecord>? response, string? error, List<string> errors)
    {
        if (response is null)
        {
            CaseList.ItemsSource = Array.Empty<CaseRecord>();
            CaseMetric.Text = "—";
            CaseNavCount.Text = "0";
            CaseListCount.Text = "Unavailable";
            if (!string.IsNullOrWhiteSpace(error))
                errors.Add($"Cases: {error}");
            ClearCaseDetails();
            return;
        }

        CaseList.ItemsSource = response.Items;
        CaseMetric.Text = response.Total.ToString();
        CaseNavCount.Text = response.Total.ToString();
        CaseListCount.Text = $"{response.Total} results";
        if (response.Items.Count > 0)
            CaseList.SelectedIndex = 0;
        else
            ClearCaseDetails();
    }

    private void ApplyProfiles(ApiList<ProfileSnapshot>? response, string? error, List<string> errors)
    {
        if (response is null)
        {
            ProfileList.ItemsSource = Array.Empty<ProfileSnapshot>();
            ProfileMetric.Text = "—";
            ProfileNavCount.Text = "0";
            if (!string.IsNullOrWhiteSpace(error))
                errors.Add($"Profiles: {error}");
            return;
        }

        ProfileList.ItemsSource = response.Items;
        var attentionCount = response.Items.Count(item => !item.SyncStatus.Equals("CURRENT", StringComparison.OrdinalIgnoreCase));
        ProfileMetric.Text = attentionCount.ToString();
        ProfileNavCount.Text = attentionCount.ToString();
    }

    private void ApplyDocuments(ApiList<SourceDocument>? response, string? error, List<string> errors)
    {
        if (response is null)
        {
            DocumentList.ItemsSource = Array.Empty<SourceDocument>();
            DocumentMetric.Text = "—";
            DocumentNavCount.Text = "0";
            DocumentListCount.Text = "Unavailable";
            if (!string.IsNullOrWhiteSpace(error))
                errors.Add($"Documents: {error}");
            ClearDocumentDetails();
            return;
        }

        DocumentList.ItemsSource = response.Items;
        DocumentMetric.Text = response.Total.ToString();
        DocumentNavCount.Text = response.Total.ToString();
        DocumentListCount.Text = $"{response.Total} documents";
        if (response.Items.Count > 0)
            DocumentList.SelectedIndex = 0;
        else
            ClearDocumentDetails();
    }

    private void SetView(string view)
    {
        CasesView.Visibility = view == "cases" ? Visibility.Visible : Visibility.Collapsed;
        ProfilesView.Visibility = view == "profiles" ? Visibility.Visible : Visibility.Collapsed;
        DocumentsView.Visibility = view == "documents" ? Visibility.Visible : Visibility.Collapsed;
        CaseStatusFilter.Visibility = view == "cases" ? Visibility.Visible : Visibility.Collapsed;
        ProfileStatusFilter.Visibility = view == "profiles" ? Visibility.Visible : Visibility.Collapsed;

        PageTitle.Text = view switch
        {
            "profiles" => "Profile review",
            "documents" => "Source library",
            _ => "Case queue"
        };
        BreadcrumbText.Text = $"CUSTOMER OPERATIONS  /  {view.ToUpperInvariant()}";
        PageSubtitle.Text = view switch
        {
            "profiles" => "Compare source-system snapshots for human review.",
            "documents" => "Search and read local source documents linked to cases.",
            _ => "Review incoming complaints and supporting details."
        };

        SetNavStyle(CasesNavButton, view == "cases");
        SetNavStyle(ProfilesNavButton, view == "profiles");
        SetNavStyle(DocumentsNavButton, view == "documents");
        _ = LoadDataAsync();
    }

    private static void SetNavStyle(Button button, bool isSelected)
    {
        button.Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(
            isSelected ? Microsoft.UI.ColorHelper.FromArgb(255, 40, 51, 35) : Microsoft.UI.Colors.Transparent);
        button.Foreground = new Microsoft.UI.Xaml.Media.SolidColorBrush(
            isSelected ? Microsoft.UI.ColorHelper.FromArgb(255, 196, 239, 121) : Microsoft.UI.ColorHelper.FromArgb(255, 170, 181, 172));
        button.BorderBrush = new Microsoft.UI.Xaml.Media.SolidColorBrush(
            isSelected ? Microsoft.UI.ColorHelper.FromArgb(255, 60, 74, 53) : Microsoft.UI.Colors.Transparent);
    }

    private void UpdateCaseDetails(CaseRecord? item)
    {
        if (item is null)
        {
            ClearCaseDetails();
            return;
        }

        CaseCategoryText.Text = item.Category.Replace('_', ' ');
        CaseReferenceText.Text = item.ComplaintRef;
        CaseStatusText.Text = FormatStatus(item.Status);
        CaseSummaryText.Text = item.CustomerSummary;
        CustomerRefText.Text = item.CustomerRef;
        AccountRefText.Text = item.AccountRef ?? "Not linked";
        ProductText.Text = item.ProductType ?? "Not specified";
        SubcategoryText.Text = string.IsNullOrWhiteSpace(item.Subcategory) ? "Not specified" : item.Subcategory.Replace('_', ' ');
        AllegationText.Text = FormatStatus(item.AllegationStatus);
        OpenedText.Text = item.OpenedDisplay;
        TargetDateText.Text = item.TargetResolutionAt?.ToLocalTime().ToString("MMM d, yyyy") ?? "Not set";
        PriorityText.Text = item.Priority;
    }

    private void ClearCaseDetails()
    {
        CaseCategoryText.Text = "No case selected";
        CaseReferenceText.Text = "";
        CaseStatusText.Text = "";
        CaseSummaryText.Text = "No case records are available from the API.";
        CustomerRefText.Text = "—";
        AccountRefText.Text = "—";
        ProductText.Text = "—";
        SubcategoryText.Text = "—";
        AllegationText.Text = "—";
        OpenedText.Text = "—";
        TargetDateText.Text = "—";
        PriorityText.Text = "—";
    }

    private void UpdateDocumentDetails(SourceDocument? item)
    {
        if (item is null)
        {
            ClearDocumentDetails();
            return;
        }

        DocumentFilenameText.Text = item.Filename;
        DocumentTitleText.Text = item.Title;
        DocumentRefsText.Text = item.RelatedRefs.Count == 0 ? "No linked references" : string.Join("  ·  ", item.RelatedRefs);
        DocumentContentText.Text = item.Content;
    }

    private void ClearDocumentDetails()
    {
        DocumentFilenameText.Text = "SOURCE DOCUMENT";
        DocumentTitleText.Text = "No document selected";
        DocumentRefsText.Text = "";
        DocumentContentText.Text = "No source documents are available from the API.";
    }

    private static string GetSelectedTag(ComboBox comboBox) =>
        comboBox.SelectedItem is ComboBoxItem item ? item.Tag?.ToString() ?? "" : "";

    private static string FormatStatus(string value) => value.Replace('_', ' ').ToLowerInvariant();

    private void CasesNavButton_Click(object sender, RoutedEventArgs e) => SetView("cases");
    private void ProfilesNavButton_Click(object sender, RoutedEventArgs e) => SetView("profiles");
    private void DocumentsNavButton_Click(object sender, RoutedEventArgs e) => SetView("documents");

    private async void RefreshButton_Click(object sender, RoutedEventArgs e) => await LoadDataAsync();
    private async void SearchButton_Click(object sender, RoutedEventArgs e) => await LoadDataAsync();

    private async void SearchBox_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key != VirtualKey.Enter)
            return;
        e.Handled = true;
        await LoadDataAsync();
    }

    private async void Filter_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (_initialized)
            await LoadDataAsync();
    }

    private void CaseList_SelectionChanged(object sender, SelectionChangedEventArgs e) =>
        UpdateCaseDetails(CaseList.SelectedItem as CaseRecord);

    private void DocumentList_SelectionChanged(object sender, SelectionChangedEventArgs e) =>
        UpdateDocumentDetails(DocumentList.SelectedItem as SourceDocument);

    private void ListView_ContainerContentChanging(
        ListViewBase sender,
        ContainerContentChangingEventArgs args)
    {
        if (args.InRecycleQueue)
            return;

        args.ItemContainer.HorizontalContentAlignment = HorizontalAlignment.Stretch;
        args.ItemContainer.Padding = new Thickness(0);
        args.ItemContainer.Margin = new Thickness(0);
    }
}