using Microsoft.Extensions.DependencyInjection;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using System;
using System.Collections.Generic;
using System.Linq;
using VoiceStudio.App.Services;
using VoiceStudio.Core.Commands;
using VoiceStudio.Core.Modules;

namespace VoiceStudio.App.Tests.Services;

/// <summary>
/// Unit tests for ModuleLoader.
/// Tests module registration, initialization, shutdown, and error handling.
/// </summary>
[TestClass]
public class ModuleLoaderTests : TestBase
{
    private ModuleLoader _loader = null!;

    [TestInitialize]
    public override void TestInitialize()
    {
        base.TestInitialize();
        _loader = new ModuleLoader();
    }

    [TestCleanup]
    public override void TestCleanup()
    {
        _loader.ShutdownAll();
        _loader = null!;
        base.TestCleanup();
    }

    #region Initial State Tests

    [TestMethod]
    public void InitialState_Modules_IsEmpty()
    {
        // Assert
        Assert.AreEqual(0, _loader.Modules.Count);
    }

    [TestMethod]
    public void InitialState_IsInitialized_IsFalse()
    {
        // Assert
        Assert.IsFalse(_loader.IsInitialized);
    }

    [TestMethod]
    public void InitialState_ServiceProvider_IsNull()
    {
        // Assert
        Assert.IsNull(_loader.ServiceProvider);
    }

    #endregion

    #region RegisterModule Generic Tests

    [TestMethod]
    public void RegisterModule_Generic_AddsModule()
    {
        // Act
        _loader.RegisterModule<TestModule>();

        // Assert
        Assert.AreEqual(1, _loader.Modules.Count);
        Assert.AreEqual("TestModule", _loader.Modules[0].ModuleId);
    }

    [TestMethod]
    public void RegisterModule_Generic_AfterInitialize_ThrowsInvalidOperationException()
    {
        // Arrange
        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        _loader.InitializeAll(services.BuildServiceProvider());

        // Act & Assert
        Assert.ThrowsException<InvalidOperationException>(() => _loader.RegisterModule<TestModule>());
    }

    [TestMethod]
    public void RegisterModule_Generic_DuplicateId_ThrowsInvalidOperationException()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();

        // Act & Assert
        Assert.ThrowsException<InvalidOperationException>(() => _loader.RegisterModule<TestModule>());
    }

    #endregion

    #region RegisterModule Instance Tests

    [TestMethod]
    public void RegisterModule_Instance_AddsModule()
    {
        // Arrange
        var module = new TestModule();

        // Act
        _loader.RegisterModule(module);

        // Assert
        Assert.AreEqual(1, _loader.Modules.Count);
        Assert.AreSame(module, _loader.Modules[0]);
    }

    [TestMethod]
    public void RegisterModule_Instance_Null_ThrowsArgumentNullException()
    {
        // Act & Assert
        Assert.ThrowsException<ArgumentNullException>(() => _loader.RegisterModule(null!));
    }

    [TestMethod]
    public void RegisterModule_Instance_AfterInitialize_ThrowsInvalidOperationException()
    {
        // Arrange
        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        _loader.InitializeAll(services.BuildServiceProvider());

        // Act & Assert
        Assert.ThrowsException<InvalidOperationException>(() => _loader.RegisterModule(new TestModule()));
    }

    [TestMethod]
    public void RegisterModule_Instance_DuplicateId_ThrowsInvalidOperationException()
    {
        // Arrange
        _loader.RegisterModule(new TestModule());

        // Act & Assert - same ID, different instance
        Assert.ThrowsException<InvalidOperationException>(() => _loader.RegisterModule(new TestModule()));
    }

    #endregion

    #region ConfigureServices Tests

    [TestMethod]
    public void ConfigureServices_CallsRegisterServicesOnAllModules()
    {
        // Arrange
        var module1 = new Mock<IUIModule>();
        module1.Setup(m => m.ModuleId).Returns("Module1");
        module1.Setup(m => m.Priority).Returns(100);

        var module2 = new Mock<IUIModule>();
        module2.Setup(m => m.ModuleId).Returns("Module2");
        module2.Setup(m => m.Priority).Returns(100);

        _loader.RegisterModule(module1.Object);
        _loader.RegisterModule(module2.Object);

        var services = new ServiceCollection();

        // Act
        _loader.ConfigureServices(services);

        // Assert
        module1.Verify(m => m.RegisterServices(services), Times.Once);
        module2.Verify(m => m.RegisterServices(services), Times.Once);
    }

    [TestMethod]
    public void ConfigureServices_SortsModulesByPriority()
    {
        // Arrange
        var lowPriority = new TestModule("LowPriority") { Priority = 200 };
        var highPriority = new TestModule("HighPriority") { Priority = 50 };
        var medPriority = new TestModule("MedPriority") { Priority = 100 };

        _loader.RegisterModule(lowPriority);
        _loader.RegisterModule(highPriority);
        _loader.RegisterModule(medPriority);

        var services = new ServiceCollection();

        // Act
        _loader.ConfigureServices(services);

        // Assert - modules should be sorted by priority
        Assert.AreEqual("HighPriority", _loader.Modules[0].ModuleId);
        Assert.AreEqual("MedPriority", _loader.Modules[1].ModuleId);
        Assert.AreEqual("LowPriority", _loader.Modules[2].ModuleId);
    }

    [TestMethod]
    public void ConfigureServices_RegistersModuleLoaderAsSingleton()
    {
        // Arrange
        var services = new ServiceCollection();
        _loader.RegisterModule<TestModule>();

        // Act
        _loader.ConfigureServices(services);
        var provider = services.BuildServiceProvider();

        // Assert
        var resolvedLoader = provider.GetService<ModuleLoader>();
        Assert.AreSame(_loader, resolvedLoader);
    }

    [TestMethod]
    public void ConfigureServices_ModuleThrowsException_WrapsInInvalidOperationException()
    {
        // Arrange
        var faultyModule = new Mock<IUIModule>();
        faultyModule.Setup(m => m.ModuleId).Returns("Faulty");
        faultyModule.Setup(m => m.Priority).Returns(100);
        faultyModule.Setup(m => m.RegisterServices(It.IsAny<IServiceCollection>()))
            .Throws(new Exception("Service registration failed"));

        _loader.RegisterModule(faultyModule.Object);
        var services = new ServiceCollection();

        // Act & Assert
        var ex = Assert.ThrowsException<InvalidOperationException>(
            () => _loader.ConfigureServices(services));
        Assert.IsTrue(ex.Message.Contains("Faulty"));
    }

    #endregion

    #region InitializeAll Tests

    [TestMethod]
    public void InitializeAll_CallsOnInitializedOnAllModules()
    {
        // Arrange
        var module1 = new Mock<IUIModule>();
        module1.Setup(m => m.ModuleId).Returns("Module1");
        module1.Setup(m => m.Priority).Returns(100);

        var module2 = new Mock<IUIModule>();
        module2.Setup(m => m.ModuleId).Returns("Module2");
        module2.Setup(m => m.Priority).Returns(100);

        _loader.RegisterModule(module1.Object);
        _loader.RegisterModule(module2.Object);

        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        var provider = services.BuildServiceProvider();

        // Act
        _loader.InitializeAll(provider);

        // Assert
        module1.Verify(m => m.OnInitialized(provider), Times.Once);
        module2.Verify(m => m.OnInitialized(provider), Times.Once);
    }

    [TestMethod]
    public void InitializeAll_SetsIsInitializedToTrue()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();
        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        var provider = services.BuildServiceProvider();

        // Act
        _loader.InitializeAll(provider);

        // Assert
        Assert.IsTrue(_loader.IsInitialized);
    }

    [TestMethod]
    public void InitializeAll_SetsServiceProvider()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();
        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        var provider = services.BuildServiceProvider();

        // Act
        _loader.InitializeAll(provider);

        // Assert
        Assert.AreSame(provider, _loader.ServiceProvider);
    }

    [TestMethod]
    public void InitializeAll_CalledTwice_ThrowsInvalidOperationException()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();
        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        var provider = services.BuildServiceProvider();
        _loader.InitializeAll(provider);

        // Act & Assert
        Assert.ThrowsException<InvalidOperationException>(() => _loader.InitializeAll(provider));
    }

    [TestMethod]
    public void InitializeAll_ModuleThrowsException_WrapsInInvalidOperationException()
    {
        // Arrange
        var faultyModule = new Mock<IUIModule>();
        faultyModule.Setup(m => m.ModuleId).Returns("Faulty");
        faultyModule.Setup(m => m.Priority).Returns(100);
        faultyModule.Setup(m => m.OnInitialized(It.IsAny<IServiceProvider>()))
            .Throws(new Exception("Initialization failed"));

        _loader.RegisterModule(faultyModule.Object);
        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        var provider = services.BuildServiceProvider();

        // Act & Assert
        var ex = Assert.ThrowsException<InvalidOperationException>(
            () => _loader.InitializeAll(provider));
        Assert.IsTrue(ex.Message.Contains("Faulty"));
    }

    #endregion

    #region ShutdownAll Tests

    [TestMethod]
    public void ShutdownAll_CallsOnShutdownOnAllModules()
    {
        // Arrange
        var module1 = new Mock<IUIModule>();
        module1.Setup(m => m.ModuleId).Returns("Module1");
        module1.Setup(m => m.Priority).Returns(100);

        var module2 = new Mock<IUIModule>();
        module2.Setup(m => m.ModuleId).Returns("Module2");
        module2.Setup(m => m.Priority).Returns(100);

        _loader.RegisterModule(module1.Object);
        _loader.RegisterModule(module2.Object);

        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        _loader.InitializeAll(services.BuildServiceProvider());

        // Act
        _loader.ShutdownAll();

        // Assert
        module1.Verify(m => m.OnShutdown(), Times.Once);
        module2.Verify(m => m.OnShutdown(), Times.Once);
    }

    [TestMethod]
    public void ShutdownAll_ModuleThrowsException_ContinuesWithOtherModules()
    {
        // Arrange
        var faultyModule = new Mock<IUIModule>();
        faultyModule.Setup(m => m.ModuleId).Returns("Faulty");
        faultyModule.Setup(m => m.Priority).Returns(50); // Higher priority = initialized first, shutdown last
        faultyModule.Setup(m => m.OnShutdown()).Throws(new Exception("Shutdown failed"));

        var goodModule = new Mock<IUIModule>();
        goodModule.Setup(m => m.ModuleId).Returns("Good");
        goodModule.Setup(m => m.Priority).Returns(100);

        _loader.RegisterModule(faultyModule.Object);
        _loader.RegisterModule(goodModule.Object);

        var services = new ServiceCollection();
        _loader.ConfigureServices(services);
        _loader.InitializeAll(services.BuildServiceProvider());

        // Act - should not throw
        _loader.ShutdownAll();

        // Assert - both modules had OnShutdown called
        faultyModule.Verify(m => m.OnShutdown(), Times.Once);
        goodModule.Verify(m => m.OnShutdown(), Times.Once);
    }

    #endregion

    #region GetModule Tests

    [TestMethod]
    public void GetModule_ById_ReturnsCorrectModule()
    {
        // Arrange
        var module = new TestModule("FindMe");
        _loader.RegisterModule(module);
        _loader.RegisterModule(new TestModule("Other"));

        // Act
        var result = _loader.GetModule("FindMe");

        // Assert
        Assert.AreSame(module, result);
    }

    [TestMethod]
    public void GetModule_ById_NotFound_ReturnsNull()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();

        // Act
        var result = _loader.GetModule("NonExistent");

        // Assert
        Assert.IsNull(result);
    }

    [TestMethod]
    public void GetModule_ByType_ReturnsCorrectModule()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();

        // Act
        var result = _loader.GetModule<TestModule>();

        // Assert
        Assert.IsNotNull(result);
        Assert.IsInstanceOfType(result, typeof(TestModule));
    }

    [TestMethod]
    public void GetModule_ByType_NotFound_ReturnsNull()
    {
        // Arrange
        _loader.RegisterModule<TestModule>();

        // Act
        var result = _loader.GetModule<AnotherTestModule>();

        // Assert
        Assert.IsNull(result);
    }

    #endregion

    #region GetAllCommands Tests

    [TestMethod]
    public void GetAllCommands_AggregatesFromAllModules()
    {
        // Arrange
        var module1Commands = new List<CommandDescriptor>
        {
            new CommandDescriptor { Id = "cmd1", Title = "Command 1" },
            new CommandDescriptor { Id = "cmd2", Title = "Command 2" }
        };
        var module2Commands = new List<CommandDescriptor>
        {
            new CommandDescriptor { Id = "cmd3", Title = "Command 3" }
        };

        var module1 = new Mock<IUIModule>();
        module1.Setup(m => m.ModuleId).Returns("Module1");
        module1.Setup(m => m.Priority).Returns(100);
        module1.Setup(m => m.GetCommands()).Returns(module1Commands);

        var module2 = new Mock<IUIModule>();
        module2.Setup(m => m.ModuleId).Returns("Module2");
        module2.Setup(m => m.Priority).Returns(100);
        module2.Setup(m => m.GetCommands()).Returns(module2Commands);

        _loader.RegisterModule(module1.Object);
        _loader.RegisterModule(module2.Object);

        // Act
        var commands = _loader.GetAllCommands().ToList();

        // Assert
        Assert.AreEqual(3, commands.Count);
    }

    #endregion

    #region GetAllResourceDictionaryUris Tests

    [TestMethod]
    public void GetAllResourceDictionaryUris_AggregatesFromAllModules()
    {
        // Arrange
        var module1Uris = new[] { "ms-appx:///Module1/Styles.xaml" };
        var module2Uris = new[] { "ms-appx:///Module2/Styles.xaml", "ms-appx:///Module2/Colors.xaml" };

        var module1 = new Mock<IUIModule>();
        module1.Setup(m => m.ModuleId).Returns("Module1");
        module1.Setup(m => m.Priority).Returns(100);
        module1.Setup(m => m.GetResourceDictionaryUris()).Returns(module1Uris);

        var module2 = new Mock<IUIModule>();
        module2.Setup(m => m.ModuleId).Returns("Module2");
        module2.Setup(m => m.Priority).Returns(100);
        module2.Setup(m => m.GetResourceDictionaryUris()).Returns(module2Uris);

        _loader.RegisterModule(module1.Object);
        _loader.RegisterModule(module2.Object);

        // Act
        var uris = _loader.GetAllResourceDictionaryUris().ToList();

        // Assert
        Assert.AreEqual(3, uris.Count);
    }

    #endregion

    #region Test Helpers

    private class TestModule : IUIModule
    {
        public string ModuleId { get; }
        public string DisplayName => ModuleId;
        public string Version => "1.0.0";
        public int Priority { get; set; } = 100;

        public TestModule()
        {
            ModuleId = "TestModule";
        }

        public TestModule(string moduleId)
        {
            ModuleId = moduleId;
        }

        public void RegisterServices(IServiceCollection services) { }
        public void OnInitialized(IServiceProvider provider) { }
        public void OnShutdown() { }
        public IEnumerable<string> GetResourceDictionaryUris() => Enumerable.Empty<string>();
        public IEnumerable<CommandDescriptor> GetCommands() => Enumerable.Empty<CommandDescriptor>();
    }

    private class AnotherTestModule : IUIModule
    {
        public string ModuleId => "AnotherTestModule";
        public string DisplayName => ModuleId;
        public string Version => "1.0.0";
        public int Priority => 100;

        public void RegisterServices(IServiceCollection services) { }
        public void OnInitialized(IServiceProvider provider) { }
        public void OnShutdown() { }
        public IEnumerable<string> GetResourceDictionaryUris() => Enumerable.Empty<string>();
        public IEnumerable<CommandDescriptor> GetCommands() => Enumerable.Empty<CommandDescriptor>();
    }

    #endregion
}
