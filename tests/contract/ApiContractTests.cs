using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Xunit;

namespace VoiceStudio.ContractTests
{
    /// <summary>
    /// Tests that validate API contracts defined in the OpenAPI schema.
    /// Client-schema alignment validation is done by Python validate-contract.py.
    /// </summary>
    public class ApiContractTests : ContractTestBase
    {
        [Fact]
        public void Schema_AllOperationsHaveOperationIds()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var missingOperationIds = new List<string>();

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (!operation.TryGetProperty("operationId", out var opId) ||
                            string.IsNullOrEmpty(opId.GetString()))
                        {
                            missingOperationIds.Add($"{operationType.ToUpper()} {path.Name}");
                        }
                    }
                }
            }

            Assert.Empty(missingOperationIds);
        }

        [Fact]
        public void Schema_OperationIdsAreValidCSharpIdentifiers()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var invalidOperationIds = new List<string>();

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("operationId", out var opId))
                        {
                            var operationId = opId.GetString();
                            if (!string.IsNullOrEmpty(operationId))
                            {
                                // Check for characters that would break C# naming
                                if (operationId.StartsWith("-") || char.IsDigit(operationId[0]))
                                {
                                    invalidOperationIds.Add($"{operationId} (invalid start)");
                                }
                                if (operationId.Contains(".") || operationId.Contains("/") ||
                                    operationId.Contains("\\") || operationId.Contains(" "))
                                {
                                    invalidOperationIds.Add($"{operationId} (invalid chars)");
                                }
                            }
                        }
                    }
                }
            }

            Assert.Empty(invalidOperationIds);
        }

        [Theory]
        [InlineData("/health")]
        [InlineData("/api/health")]
        public void Schema_HealthEndpointExists(string path)
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var hasPath = paths.TryGetProperty(path, out _);

            // At least one health endpoint should exist
            if (!hasPath && path == "/health")
            {
                Assert.True(paths.TryGetProperty("/api/health", out _),
                    "No health endpoint found (neither /health nor /api/health)");
            }
        }

        [Fact]
        public void Schema_AllOperationsHaveResponses()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var missingResponses = new List<string>();

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (!operation.TryGetProperty("responses", out var responses) ||
                            responses.ValueKind != JsonValueKind.Object)
                        {
                            missingResponses.Add($"{operationType.ToUpper()} {path.Name}");
                        }
                    }
                }
            }

            Assert.Empty(missingResponses);
        }

        [Fact]
        public void Schema_AllOperationsHaveSuccessResponse()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var missingSuccessResponse = new List<string>();

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("responses", out var responses))
                        {
                            var successCodes = new[] { "200", "201", "204" };
                            var hasSuccess = successCodes.Any(code =>
                                responses.TryGetProperty(code, out _));

                            if (!hasSuccess)
                            {
                                missingSuccessResponse.Add($"{operationType.ToUpper()} {path.Name}");
                            }
                        }
                    }
                }
            }

            Assert.Empty(missingSuccessResponse);
        }

        [Fact]
        public void Schema_RequestBodiesHaveContentType()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var missingContentType = new List<string>();

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "post", "put", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("requestBody", out var requestBody))
                        {
                            if (!requestBody.TryGetProperty("content", out var content) ||
                                content.ValueKind != JsonValueKind.Object)
                            {
                                missingContentType.Add($"{operationType.ToUpper()} {path.Name}");
                            }
                        }
                    }
                }
            }

            Assert.Empty(missingContentType);
        }

        [Fact]
        public void Schema_ModelsHaveTypeDefinitions()
        {
            if (!OpenApiSchema.RootElement.TryGetProperty("components", out var components))
                return;

            if (!components.TryGetProperty("schemas", out var schemas))
                return;

            var untypedSchemas = new List<string>();

            foreach (var schema in schemas.EnumerateObject())
            {
                var schemaValue = schema.Value;

                var hasType = schemaValue.TryGetProperty("type", out _) ||
                              schemaValue.TryGetProperty("$ref", out _) ||
                              schemaValue.TryGetProperty("allOf", out _) ||
                              schemaValue.TryGetProperty("anyOf", out _) ||
                              schemaValue.TryGetProperty("oneOf", out _);

                if (!hasType)
                {
                    untypedSchemas.Add(schema.Name);
                }
            }

            // Allow some untyped schemas for backward compatibility (up to 10%)
            var totalSchemas = schemas.EnumerateObject().Count();
            if (untypedSchemas.Count > totalSchemas * 0.1)
            {
                Assert.Fail($"Too many untyped schemas ({untypedSchemas.Count}/{totalSchemas}): " +
                    string.Join(", ", untypedSchemas.Take(10)));
            }
        }

        [Fact]
        public void Schema_OperationsHaveUniqueOperationIds()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            var operationIds = new Dictionary<string, List<string>>();

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("operationId", out var opId))
                        {
                            var operationId = opId.GetString();
                            if (!string.IsNullOrEmpty(operationId))
                            {
                                if (!operationIds.ContainsKey(operationId))
                                    operationIds[operationId] = new List<string>();

                                operationIds[operationId].Add($"{operationType.ToUpper()} {path.Name}");
                            }
                        }
                    }
                }
            }

            var duplicates = operationIds.Where(kv => kv.Value.Count > 1).ToList();
            if (duplicates.Any())
            {
                var message = string.Join("\n", duplicates.Select(d =>
                    $"{d.Key}: {string.Join(", ", d.Value)}"));
                Assert.Fail($"Duplicate operationIds found:\n{message}");
            }
        }
    }
}
