# MCP Bridge Layer

This layer normalizes responses from MCP servers into shared contract schemas.

## MCP Servers

- Figma (design tokens)
- Magic UI
- Flux UI
- Shadcn
- TTS/VC models
- Whisper
- **PDF Unlocker** - Read and extract text from protected/unprotected PDFs

## Integration

The bridge layer calls MCP servers and transforms their responses into the standardized contract format defined in `shared/contracts/`.

## PDF Unlocker Integration

The PDF Unlocker MCP server (`mcp-unlock-pdf`) has been integrated into VoiceStudio to enable:

- **Text Extraction**: Extract text from PDFs for voice synthesis
- **Protected PDF Support**: Read password-protected PDFs
- **Page Selection**: Extract text from specific pages
- **Metadata Extraction**: Get PDF metadata (title, author, etc.)

### Usage

The PDF unlocker is available via:
- **API Route**: `/api/pdf/*` endpoints (see `backend/api/routes/pdf.py`)
- **MCP Client**: `backend/mcp_bridge/pdf_unlocker_client.py`

### Server Location

The MCP server is located at: `backend/mcp_servers/mcp-unlock-pdf/`

### Dependencies

The client uses PyPDF2 directly for performance. Ensure PyPDF2 is installed:
```bash
pip install PyPDF2>=3.0.1
```

