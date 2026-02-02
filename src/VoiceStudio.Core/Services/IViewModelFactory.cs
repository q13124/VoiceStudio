using System;

namespace VoiceStudio.Core.Services
{
    /// <summary>
    /// Factory for creating ViewModel instances with dependency injection.
    /// Enables ViewModel-first instantiation pattern where Views receive pre-built ViewModels.
    /// </summary>
    /// <remarks>
    /// Use cases:
    /// - Views that need parameterized ViewModels
    /// - Navigation services that create ViewModels before Views
    /// - Unit testing with mock ViewModels
    /// </remarks>
    public interface IViewModelFactory
    {
        /// <summary>
        /// Creates a ViewModel of the specified type using the DI container.
        /// </summary>
        /// <typeparam name="TViewModel">The ViewModel type to create.</typeparam>
        /// <returns>A fully initialized ViewModel instance.</returns>
        TViewModel Create<TViewModel>() where TViewModel : class;

        /// <summary>
        /// Creates a ViewModel of the specified type using the DI container.
        /// </summary>
        /// <param name="viewModelType">The ViewModel type to create.</param>
        /// <returns>A fully initialized ViewModel instance.</returns>
        object Create(Type viewModelType);

        /// <summary>
        /// Creates a ViewModel with additional constructor parameters.
        /// Useful for ViewModels that need runtime-specific data.
        /// </summary>
        /// <typeparam name="TViewModel">The ViewModel type to create.</typeparam>
        /// <param name="parameters">Additional constructor parameters.</param>
        /// <returns>A fully initialized ViewModel instance.</returns>
        TViewModel CreateWithParameters<TViewModel>(params object[] parameters) where TViewModel : class;
    }
}
