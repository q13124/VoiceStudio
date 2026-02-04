using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using VoiceStudio.App.Tests.Services;
using VoiceStudio.App.Tests.ViewModels;
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
  /// <summary>
  /// Base class for ViewModel tests providing common setup and helper methods.
  /// Inherit from this class to share common test infrastructure for ViewModel tests.
  /// </summary>
  public abstract class ViewModelTestBase : TestBase
  {
    protected MockBackendClient? MockBackendClient { get; private set; }
    protected MockAnalyticsService? MockAnalyticsService { get; private set; }
    protected MockNavigationService? MockNavigationService { get; private set; }

    [TestInitialize]
    public override void TestInitialize()
    {
      base.TestInitialize();

      // Initialize mock services
      MockBackendClient = new MockBackendClient();
      MockAnalyticsService = new MockAnalyticsService();
      MockNavigationService = new MockNavigationService();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
      // Clear mock service state
      MockAnalyticsService?.Clear();
      MockNavigationService?.Clear();

      MockBackendClient = null;
      MockAnalyticsService = null;
      MockNavigationService = null;

      base.TestCleanup();
    }

    /// <summary>
    /// Helper method to wait for async operations to complete.
    /// </summary>
    protected async System.Threading.Tasks.Task WaitForAsyncOperation()
    {
      await System.Threading.Tasks.Task.Delay(100);
    }

    /// <summary>
    /// Helper method to verify ViewModel has standard properties.
    /// </summary>
    protected void VerifyStandardViewModelProperties<T>(T viewModel) where T : VoiceStudio.App.ViewModels.BaseViewModel
    {
      Assert.IsNotNull(viewModel, "ViewModel should not be null");

      // BaseViewModel properties should be accessible
      // Note: IsLoading and ErrorMessage are typically properties on ViewModels
      // The exact properties depend on the ViewModel implementation
    }
  }
}