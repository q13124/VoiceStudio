using System.Collections.ObjectModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls;

public sealed partial class SkeletonScreen : UserControl
{
    public static readonly DependencyProperty SkeletonItemsProperty =
        DependencyProperty.Register(
            nameof(SkeletonItems),
            typeof(ObservableCollection<int>),
            typeof(SkeletonScreen),
            new PropertyMetadata(new ObservableCollection<int> { 1, 2, 3, 4, 5, 6 }));

    public ObservableCollection<int> SkeletonItems
    {
        get => (ObservableCollection<int>)GetValue(SkeletonItemsProperty);
        set => SetValue(SkeletonItemsProperty, value);
    }

    public SkeletonScreen()
    {
        this.InitializeComponent();
    }
}

