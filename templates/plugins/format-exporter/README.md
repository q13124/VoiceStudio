# {{DISPLAY_NAME}} Format Exporter Template

Template for building an `ExporterPlugin` wrapper around
`backend.core.audio.conversion.AudioConversionService`.

## Includes

- Exporter plugin contract implementation
- FastAPI export endpoint
- Base64 WAV input handling
- Output format conversion path

## Typical customizations

- Set `supported_formats` for your target encoder
- Map quality options (bitrate, sample rate, channels)
- Add format-specific validation in `export()`
