using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using VoiceStudio.App.ViewModels;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.Tests.ViewModels
{
    /// <summary>
    /// Unit tests for PronunciationLexiconViewModel.
    /// Source: PronunciationLexiconViewModel.cs
    /// </summary>
    [TestClass]
    public class PronunciationLexiconViewModelTests : ViewModelTestBase
    {
        private Mock<IBackendClient>? _mockBackendClient;

        [TestInitialize]
        public override void TestInitialize()
        {
            base.TestInitialize();
            _mockBackendClient = new Mock<IBackendClient>();
        }

        private PronunciationLexiconViewModel CreateViewModel()
        {
            return new PronunciationLexiconViewModel(MockContext!, _mockBackendClient!.Object);
        }

        #region Construction and Initialization Tests

        [TestMethod]
        public void Constructor_WithValidDependencies_CreatesInstance()
        {
            // Arrange & Act
            var viewModel = CreateViewModel();

            // Assert
            Assert.IsNotNull(viewModel);
            Assert.AreEqual("pronunciation-lexicon", viewModel.PanelId);
            Assert.IsNotNull(viewModel.Entries);
            Assert.IsNotNull(viewModel.AvailableLanguages);
        }

        [TestMethod]
        public void Constructor_WithNullContext_ThrowsArgumentNullException()
        {
            Assert.ThrowsException<ArgumentNullException>(() =>
                new PronunciationLexiconViewModel(null!, _mockBackendClient!.Object));
        }

        [TestMethod]
        public void Constructor_WithNullBackendClient_ThrowsArgumentNullException()
        {
            Assert.ThrowsException<ArgumentNullException>(() =>
                new PronunciationLexiconViewModel(MockContext!, null!));
        }

        [TestMethod]
        public void Constructor_InitializesDefaultLanguages()
        {
            // Arrange & Act
            var viewModel = CreateViewModel();

            // Assert
            Assert.IsNotNull(viewModel.AvailableLanguages);
            Assert.IsTrue(viewModel.AvailableLanguages.Count >= 5);
            CollectionAssert.Contains(viewModel.AvailableLanguages, "en");
            CollectionAssert.Contains(viewModel.AvailableLanguages, "es");
            CollectionAssert.Contains(viewModel.AvailableLanguages, "fr");
        }

        [TestMethod]
        public void Constructor_InitializesEmptyCollections()
        {
            // Arrange & Act
            var viewModel = CreateViewModel();

            // Assert
            Assert.IsNotNull(viewModel.Entries);
            Assert.AreEqual(0, viewModel.Entries.Count);
            Assert.IsNotNull(viewModel.Conflicts);
            Assert.IsNotNull(viewModel.ValidationErrors);
        }

        #endregion

        #region Property Tests

        [TestMethod]
        public void Entries_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.Entries))
                    propertyChanged = true;
            };

            // Act
            viewModel.Entries = new ObservableCollection<PronunciationLexiconEntryItem>();

            // Assert
            Assert.IsTrue(propertyChanged);
        }

        [TestMethod]
        public void AvailableLanguages_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.AvailableLanguages))
                    propertyChanged = true;
            };

            // Act
            viewModel.AvailableLanguages = new ObservableCollection<string> { "en", "de" };

            // Assert
            Assert.IsTrue(propertyChanged);
        }

        [TestMethod]
        public void PhonemeConfidence_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.PhonemeConfidence))
                    propertyChanged = true;
            };

            // Act
            viewModel.PhonemeConfidence = 0.95f;

            // Assert
            Assert.IsTrue(propertyChanged);
            Assert.AreEqual(0.95f, viewModel.PhonemeConfidence);
        }

        [TestMethod]
        public void Conflicts_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.Conflicts))
                    propertyChanged = true;
            };

            // Act
            viewModel.Conflicts = new ObservableCollection<string> { "Conflict1" };

            // Assert
            Assert.IsTrue(propertyChanged);
        }

        [TestMethod]
        public void ValidationErrors_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.ValidationErrors))
                    propertyChanged = true;
            };

            // Act
            viewModel.ValidationErrors = new ObservableCollection<string> { "Error1" };

            // Assert
            Assert.IsTrue(propertyChanged);
        }

        [TestMethod]
        public void IsValid_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.IsValid))
                    propertyChanged = true;
            };

            // Act
            viewModel.IsValid = false;

            // Assert
            Assert.IsTrue(propertyChanged);
            Assert.IsFalse(viewModel.IsValid);
        }

        [TestMethod]
        public void NewWord_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.NewWord))
                    propertyChanged = true;
            };

            // Act
            viewModel.NewWord = "hello";

            // Assert
            Assert.IsTrue(propertyChanged);
            Assert.AreEqual("hello", viewModel.NewWord);
        }

        [TestMethod]
        public void NewPronunciation_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.NewPronunciation))
                    propertyChanged = true;
            };

            // Act
            viewModel.NewPronunciation = "HH AH L OW";

            // Assert
            Assert.IsTrue(propertyChanged);
            Assert.AreEqual("HH AH L OW", viewModel.NewPronunciation);
        }

        [TestMethod]
        public void SelectedLanguage_WhenSet_RaisesPropertyChanged()
        {
            // Arrange
            var viewModel = CreateViewModel();
            var propertyChanged = false;
            viewModel.PropertyChanged += (s, e) =>
            {
                if (e.PropertyName == nameof(viewModel.SelectedLanguage))
                    propertyChanged = true;
            };

            // Act
            viewModel.SelectedLanguage = "fr";

            // Assert
            Assert.IsTrue(propertyChanged);
            Assert.AreEqual("fr", viewModel.SelectedLanguage);
        }

        #endregion

        #region Panel Interface Tests

        [TestMethod]
        public void PanelId_ReturnsCorrectValue()
        {
            var viewModel = CreateViewModel();
            Assert.AreEqual("pronunciation-lexicon", viewModel.PanelId);
        }

        [TestMethod]
        public void DisplayName_ReturnsNonEmptyString()
        {
            var viewModel = CreateViewModel();
            Assert.IsFalse(string.IsNullOrEmpty(viewModel.DisplayName));
        }

        [TestMethod]
        public void Region_ReturnsRightRegion()
        {
            var viewModel = CreateViewModel();
            Assert.AreEqual(VoiceStudio.Core.Panels.PanelRegion.Right, viewModel.Region);
        }

        #endregion

        #region Error Handling Tests

        [TestMethod]
        public void ViewModel_WhenErrorOccurs_HandlesGracefully()
        {
            // Arrange
            var viewModel = CreateViewModel();

            // Act - setting null values should not throw
            viewModel.NewWord = null;
            viewModel.NewPronunciation = null;
            viewModel.SearchQuery = null;
            viewModel.SelectedLanguage = null;
            viewModel.SelectedEntry = null;

            // Assert
            Assert.IsNotNull(viewModel);
            Assert.IsNotNull(viewModel.Entries);
            Assert.IsNotNull(viewModel.AvailableLanguages);
        }

        #endregion
    }
}