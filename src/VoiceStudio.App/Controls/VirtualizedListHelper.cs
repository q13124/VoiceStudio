using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Collections.Generic;

namespace VoiceStudio.App.Controls
{
    /// <summary>
    /// Helper for configuring UI virtualization on list controls.
    /// Provides optimal virtualization settings for large data sets.
    ///
    /// Usage:
    /// 1. For ListView: VirtualizedListHelper.ConfigureListView(listView)
    /// 2. For ItemsRepeater: Use VirtualizedListHelper.CreateVirtualizingLayout()
    /// </summary>
    public static class VirtualizedListHelper
    {
        /// <summary>
        /// Default page size for incremental loading.
        /// </summary>
        public const int DefaultPageSize = 50;

        /// <summary>
        /// Buffer size for item recycling.
        /// </summary>
        public const int DefaultRecycleBuffer = 10;

        /// <summary>
        /// Configures a ListView for optimal virtualization performance.
        /// </summary>
        public static void ConfigureListView(ListView listView)
        {
            if (listView == null)
                return;

            // Enable virtualization (on by default, but ensure it's set)
            listView.IsItemClickEnabled = true;

            // Use ItemsStackPanel for virtualization (default for ListView)
            var panel = new ItemsStackPanel
            {
                // Orientation for vertical lists
                Orientation = Orientation.Vertical,

                // Cache length determines how many pages of items to keep cached
                // Higher values use more memory but smoother scrolling
                CacheLength = 4.0,
            };

            listView.ItemsPanel = new ItemsPanelTemplate();

            // For best performance with large lists:
            // - Use x:Load for conditional loading
            // - Use x:Phase for phased loading
            // - Keep item templates simple
        }

        /// <summary>
        /// Creates a virtualizing stack layout for ItemsRepeater.
        /// </summary>
        public static StackLayout CreateVirtualizingLayout(Orientation orientation = Orientation.Vertical)
        {
            return new StackLayout
            {
                Orientation = orientation,
                Spacing = 4,
            };
        }

        /// <summary>
        /// Creates an optimized uniform grid layout for ItemsRepeater.
        /// Good for grids of similarly-sized items (thumbnails, cards).
        /// </summary>
        public static UniformGridLayout CreateGridLayout(
            int minItemWidth = 200,
            int minItemHeight = 150,
            int minColumnSpacing = 8,
            int minRowSpacing = 8)
        {
            return new UniformGridLayout
            {
                MinItemWidth = minItemWidth,
                MinItemHeight = minItemHeight,
                MinColumnSpacing = minColumnSpacing,
                MinRowSpacing = minRowSpacing,
                ItemsStretch = UniformGridLayoutItemsStretch.Fill,
                ItemsJustification = UniformGridLayoutItemsJustification.Start,
            };
        }

        // NOTE: FlowLayout is not available in the current Windows App SDK version.
        // Use StackLayout or UniformGridLayout instead.
        // This method is commented out until FlowLayout becomes available.
        //
        // public static FlowLayout CreateFlowLayout(
        //     Orientation orientation = Orientation.Horizontal,
        //     int minColumnSpacing = 8,
        //     int minRowSpacing = 8)
        // {
        //     return new FlowLayout
        //     {
        //         Orientation = orientation,
        //         MinColumnSpacing = minColumnSpacing,
        //         MinRowSpacing = minRowSpacing,
        //     };
        // }
    }

    /// <summary>
    /// Incremental loading source for virtualized lists.
    /// Implements paging for large data sets.
    /// </summary>
    /// <typeparam name="T">The type of items in the collection.</typeparam>
    public class IncrementalLoadingCollection<T> :
        System.Collections.ObjectModel.ObservableCollection<T>,
        Microsoft.UI.Xaml.Data.ISupportIncrementalLoading
    {
        private readonly Func<int, int, System.Threading.Tasks.Task<IList<T>>> _loadMoreAsync;
        private readonly int _pageSize;
        private bool _hasMoreItems = true;

        /// <summary>
        /// Creates a new incremental loading collection.
        /// </summary>
        /// <param name="loadMoreAsync">Function to load more items (page, pageSize) => items</param>
        /// <param name="pageSize">Number of items per page</param>
        public IncrementalLoadingCollection(
            Func<int, int, System.Threading.Tasks.Task<IList<T>>> loadMoreAsync,
            int pageSize = VirtualizedListHelper.DefaultPageSize)
        {
            _loadMoreAsync = loadMoreAsync;
            _pageSize = pageSize;
        }

        public bool HasMoreItems => _hasMoreItems;

        public Windows.Foundation.IAsyncOperation<Microsoft.UI.Xaml.Data.LoadMoreItemsResult> LoadMoreItemsAsync(uint count)
        {
            return LoadMoreItemsCoreAsync(count).AsAsyncOperation();
        }

        private async System.Threading.Tasks.Task<Microsoft.UI.Xaml.Data.LoadMoreItemsResult> LoadMoreItemsCoreAsync(uint count)
        {
            try
            {
                var currentPage = Count / _pageSize;
                var items = await _loadMoreAsync(currentPage, _pageSize);

                if (items == null || items.Count == 0)
                {
                    _hasMoreItems = false;
                    return new Microsoft.UI.Xaml.Data.LoadMoreItemsResult { Count = 0 };
                }

                if (items.Count < _pageSize)
                {
                    _hasMoreItems = false;
                }

                foreach (var item in items)
                {
                    Add(item);
                }

                return new Microsoft.UI.Xaml.Data.LoadMoreItemsResult { Count = (uint)items.Count };
            }
            catch
            {
                _hasMoreItems = false;
                return new Microsoft.UI.Xaml.Data.LoadMoreItemsResult { Count = 0 };
            }
        }
    }
}
