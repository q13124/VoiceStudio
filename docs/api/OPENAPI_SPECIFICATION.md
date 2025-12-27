# VoiceStudio Quantum+ OpenAPI Specification

Complete guide to accessing and using the VoiceStudio Quantum+ OpenAPI/Swagger specification.

## Overview

VoiceStudio Quantum+ uses FastAPI, which automatically generates an OpenAPI 3.0 specification from the route definitions and Pydantic models. The specification is always up-to-date and reflects the current API structure.

## Accessing the OpenAPI Specification

### Interactive Documentation (Swagger UI)

**URL:** `http://localhost:8000/docs`

The Swagger UI provides an interactive interface to explore and test all API endpoints.

**Features:**
- Browse all endpoints by category
- View request/response schemas
- Test endpoints directly from the browser
- See example requests and responses
- View authentication requirements

### Alternative Documentation (ReDoc)

**URL:** `http://localhost:8000/redoc`

ReDoc provides an alternative documentation interface with a clean, readable format.

### OpenAPI JSON Schema

**URL:** `http://localhost:8000/openapi.json`

The raw OpenAPI 3.0 JSON schema. This can be:
- Imported into API testing tools (Postman, Insomnia)
- Used to generate client SDKs
- Validated against OpenAPI specification
- Used for API mocking

## Exporting the OpenAPI Specification

### Method 1: Direct Download

```bash
# Download the OpenAPI spec
curl http://localhost:8000/openapi.json -o openapi.json
```

### Method 2: Using Python Script

See `scripts/export_openapi.py` for an automated export script.

### Method 3: From Running Server

1. Start the backend server:
   ```bash
   cd backend
   python -m api.main
   ```

2. Access the OpenAPI spec:
   - Browser: Navigate to `http://localhost:8000/openapi.json`
   - Command line: `curl http://localhost:8000/openapi.json`

## Using the OpenAPI Specification

### Generate Client SDKs

#### Python Client

```bash
# Install openapi-generator
npm install @openapitools/openapi-generator-cli -g

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./generated/python-client
```

#### TypeScript/JavaScript Client

```bash
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./generated/typescript-client
```

#### C# Client

```bash
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g csharp \
  -o ./generated/csharp-client
```

### Import into API Testing Tools

#### Postman

1. Open Postman
2. Click "Import"
3. Select "Link" tab
4. Enter: `http://localhost:8000/openapi.json`
5. Click "Continue" and "Import"

#### Insomnia

1. Open Insomnia
2. Click "Create" → "Import/Export"
3. Select "Import Data" → "From URL"
4. Enter: `http://localhost:8000/openapi.json`
5. Click "Import"

### Validate the Specification

```bash
# Install swagger-cli
npm install -g @apidevtools/swagger-cli

# Validate the spec
swagger-cli validate http://localhost:8000/openapi.json
```

## OpenAPI Specification Details

### Version

- **OpenAPI Version:** 3.0.0
- **API Version:** 1.0

### Server Information

```json
{
  "servers": [
    {
      "url": "http://localhost:8000",
      "description": "Development server"
    }
  ]
}
```

### Endpoint Categories

The OpenAPI spec includes all endpoints organized by tags:

- **Core:** Health checks, root endpoint
- **Voice Profiles:** Profile management
- **Voice Synthesis:** Voice cloning and synthesis
- **Projects:** Project management
- **Tracks and Clips:** Timeline editing
- **Audio Analysis:** Audio analysis tools
- **Effects:** Audio effects processing
- **Mixer:** Professional mixer controls
- **Macros:** Automation and macros
- **Training:** Voice model training
- **Batch Processing:** Batch synthesis
- **Transcription:** Speech-to-text
- **Models:** Model management
- **Settings:** Application settings
- **Backup & Restore:** Backup operations
- **Tag Management:** Tag system
- **Quality Improvement Features:** Quality enhancement endpoints
- **Quality Testing & Comparison:** A/B testing, benchmarking, recommendations

### New Endpoints (Latest Updates)

The following endpoints have been added to the OpenAPI specification:

#### A/B Testing

- `POST /api/eval/abx/start` - Start A/B testing evaluation
- `GET /api/eval/abx/results` - Get A/B testing results

#### Engine Recommendation

- `GET /api/quality/engine-recommendation` - Get engine recommendation based on quality requirements

#### Quality Benchmarking

- `POST /api/quality/benchmark` - Run quality benchmark across multiple engines

#### Quality Dashboard

- `GET /api/quality/dashboard` - Get quality metrics dashboard data

## Model Schemas

All request and response models are defined using Pydantic and automatically included in the OpenAPI spec:

### Quality Testing Models

- `AbxStartRequest` - A/B test start request
- `AbxResult` - A/B test result
- `BenchmarkRequest` - Benchmark request
- `BenchmarkResponse` - Benchmark response
- `BenchmarkResult` - Individual engine benchmark result
- `EngineRecommendationResponse` - Engine recommendation response
- `QualityDashboardResponse` - Quality dashboard response

### Quality Improvement Models

- `MultiPassSynthesisRequest` - Multi-pass synthesis request
- `MultiPassSynthesisResponse` - Multi-pass synthesis response
- `ArtifactRemovalRequest` - Artifact removal request
- `ArtifactRemovalResponse` - Artifact removal response
- And many more...

## Updating the OpenAPI Specification

The OpenAPI specification is automatically generated by FastAPI. To update it:

1. **Add New Endpoints:** Define routes in `backend/api/routes/`
2. **Add Request/Response Models:** Define Pydantic models
3. **Add Documentation:** Use docstrings and Pydantic field descriptions
4. **Restart Server:** The spec updates automatically

### Best Practices

1. **Use Pydantic Models:** All request/response bodies should use Pydantic BaseModel
2. **Add Descriptions:** Use field descriptions and docstrings
3. **Use Type Hints:** FastAPI uses type hints for schema generation
4. **Add Examples:** Use Pydantic Field examples for better documentation
5. **Tag Endpoints:** Use router tags to organize endpoints

## Example: Adding a New Endpoint

```python
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/example", tags=["example"])

class ExampleRequest(BaseModel):
    """Example request model."""
    text: str = Field(..., description="Text to process", example="Hello, world!")
    count: int = Field(1, ge=1, le=100, description="Number of times to process")

class ExampleResponse(BaseModel):
    """Example response model."""
    result: str = Field(..., description="Processed result")
    processed_count: int = Field(..., description="Number of times processed")

@router.post("/process", response_model=ExampleResponse)
async def process_example(request: ExampleRequest):
    """
    Process example text.
    
    This endpoint processes the provided text and returns a result.
    """
    return ExampleResponse(
        result=f"Processed: {request.text}",
        processed_count=request.count
    )
```

This will automatically appear in:
- OpenAPI spec at `/openapi.json`
- Swagger UI at `/docs`
- ReDoc at `/redoc`

## Troubleshooting

### OpenAPI Spec Not Updating

1. **Restart the server:** Changes require a server restart
2. **Check route imports:** Ensure routes are imported in `main.py`
3. **Check model definitions:** Verify Pydantic models are correctly defined
4. **Check tags:** Ensure router tags are set

### Invalid OpenAPI Spec

1. **Validate the spec:** Use `swagger-cli validate`
2. **Check for circular references:** Pydantic models should not have circular imports
3. **Check type hints:** Ensure all types are properly annotated
4. **Check FastAPI version:** Ensure FastAPI is up-to-date

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

---

**Last Updated:** 2025-01-27  
**OpenAPI Version:** 3.0.0  
**API Version:** 1.0

