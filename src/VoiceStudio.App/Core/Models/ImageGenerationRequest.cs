using System;

namespace VoiceStudio.Core.Models
{
    public class ImageGenerateRequest
    {
        public string Engine { get; set; } = "sdxl";
        public string Prompt { get; set; } = string.Empty;
        public string NegativePrompt { get; set; } = string.Empty;
        public int Width { get; set; } = 512;
        public int Height { get; set; } = 512;
        public int Steps { get; set; } = 20;
        public double CfgScale { get; set; } = 7.0;
        public string? Sampler { get; set; }
        public int? Seed { get; set; }
        public bool EnablePreprocessing { get; set; } = false;
        public string? DenoisingMethod { get; set; }
        public string? EnhancementMethod { get; set; }
        public int EnhancementStrength { get; set; } = 50;
    }

    public class ImageGenerateResponse
    {
        public string ImageId { get; set; } = string.Empty;
        public string ImageUrl { get; set; } = string.Empty;
        public string ImageBase64 { get; set; } = string.Empty;
        public int Width { get; set; }
        public int Height { get; set; }
        public string Format { get; set; } = "png";
    }

    public class ImageUpscaleRequest
    {
        public string? Engine { get; set; } = "realesrgan";
        public string? ImageId { get; set; }
        public int Scale { get; set; } = 4;
    }

    public class ImageUpscaleResponse
    {
        public string ImageId { get; set; } = string.Empty;
        public string ImageUrl { get; set; } = string.Empty;
        public string ImageBase64 { get; set; } = string.Empty;
        public int Width { get; set; }
        public int Height { get; set; }
        public int Scale { get; set; }
    }
}

