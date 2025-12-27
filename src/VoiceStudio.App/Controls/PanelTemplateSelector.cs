using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Controls
{
    public sealed class PanelTemplateSelector : DataTemplateSelector
    {
        public DataTemplate TextSpeechEditorTemplate { get; set; } = default!;
        public DataTemplate ProsodyTemplate { get; set; } = default!;
        public DataTemplate SpatialTemplate { get; set; } = default!;
        public DataTemplate MixAssistantTemplate { get; set; } = default!;
        public DataTemplate StyleTransferTemplate { get; set; } = default!;
        public DataTemplate EmbeddingExplorerTemplate { get; set; } = default!;
        public DataTemplate AssistantTemplate { get; set; } = default!;
        public DataTemplate LexiconTemplate { get; set; } = default!;
        public DataTemplate VoiceMorphTemplate { get; set; } = default!;
        public DataTemplate VideoGenTemplate { get; set; } = default!;
        public DataTemplate VideoEditTemplate { get; set; } = default!;

        protected override DataTemplate SelectTemplateCore(object item)
        {
            if (item is PanelDescriptor d)
            {
                switch (d.PanelId)
                {
                    case "TextSpeechEditor": return TextSpeechEditorTemplate;
                    case "ProsodyPhoneme": return ProsodyTemplate;
                    case "SpatialStage": return SpatialTemplate;
                    case "MixAssistant": return MixAssistantTemplate;
                    case "StyleTransfer": return StyleTransferTemplate;
                    case "EmbeddingExplorer": return EmbeddingExplorerTemplate;
                    case "Assistant": return AssistantTemplate;
                    case "Lexicon": return LexiconTemplate;
                    case "VoiceMorph": return VoiceMorphTemplate;
                    case "VideoGen": return VideoGenTemplate;
                    case "VideoEdit": return VideoEditTemplate;
                }
            }
            return base.SelectTemplateCore(item);
        }
    }
}

