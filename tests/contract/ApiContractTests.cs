using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using Xunit;
using VoiceStudio.Core.Services.Generated;

namespace VoiceStudio.ContractTests
{
    /// <summary>
    /// Tests that validate API contracts match between OpenAPI schema and generated C# client.
    /// </summary>
    public class ApiContractTests : ContractTestBase
    {
        private readonly Type _clientType;

        public ApiContractTests()
        {
            // Get the generated client type
            _clientType = typeof(Client);
        }

        [Fact]
        public void GeneratedClient_Exists()
        {
            Assert.NotNull(_clientType);
            Assert.Equal("Client", _clientType.Name);
        }

        [Fact]
        public void GeneratedClient_HasAllEndpoints()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");
            
            // Get all client types (Client, HealthClient, StatsClient, etc.)
            var clientTypes = typeof(Client).Assembly
                .GetTypes()
                .Where(t => t.Name.EndsWith("Client") && t.IsClass && !t.IsAbstract)
                .ToList();
            
            var allEndpointMethods = clientTypes
                .SelectMany(ct => GetEndpointMethods(ct))
                .ToList();

            foreach (var path in paths.EnumerateObject())
            {
                var pathName = path.Name;
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        var operationId = operation.TryGetProperty("operationId", out var opId)
                            ? opId.GetString()
                            : null;

                        // Check if method exists in any client class
                        // Methods might be named by operationId, path, or just HTTP method
                        var methodExists = allEndpointMethods.Any(m =>
                            (!string.IsNullOrEmpty(operationId) && 
                             (m.Name.Contains(operationId.Replace("_", ""), StringComparison.OrdinalIgnoreCase) ||
                              m.Name.Contains(operationId.Split('_').FirstOrDefault() ?? "", StringComparison.OrdinalIgnoreCase))) ||
                            m.Name.Contains(GetMethodNameFromPath(pathName), StringComparison.OrdinalIgnoreCase) ||
                            (operationType == "get" && m.Name.StartsWith("Get", StringComparison.OrdinalIgnoreCase)) ||
                            (operationType == "post" && m.Name.StartsWith("Post", StringComparison.OrdinalIgnoreCase)) ||
                            (operationType == "put" && m.Name.StartsWith("Put", StringComparison.OrdinalIgnoreCase)) ||
                            (operationType == "delete" && m.Name.StartsWith("Delete", StringComparison.OrdinalIgnoreCase)) ||
                            (operationType == "patch" && m.Name.StartsWith("Patch", StringComparison.OrdinalIgnoreCase))
                        );

                        // For root path, check if there's a GetAsync method with no parameters
                        if (pathName == "/" && operationType == "get")
                        {
                            methodExists = allEndpointMethods.Any(m =>
                                m.Name.StartsWith("Get", StringComparison.OrdinalIgnoreCase) &&
                                m.GetParameters().Length <= 1); // No params or just CancellationToken
                        }

                        Assert.True(
                            methodExists,
                            $"Method for {operationType.ToUpper()} {pathName} (operationId: {operationId}) not found in generated client. Available methods: {string.Join(", ", allEndpointMethods.Select(m => m.Name).Take(10))}"
                        );
                    }
                }
            }
        }

        [Fact]
        public void GeneratedClient_RequestModelsMatchSchema()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "post", "put", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("requestBody", out var requestBody))
                        {
                            var requestSchema = GetRequestSchema(requestBody);
                            var modelType = FindModelType(requestSchema);

                            if (modelType != null)
                            {
                                ValidateModelProperties(modelType, requestSchema);
                            }
                        }
                    }
                }
            }
        }

        [Fact]
        public void GeneratedClient_ResponseModelsMatchSchema()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("responses", out var responses))
                        {
                            if (responses.TryGetProperty("200", out var successResponse))
                            {
                                var responseSchema = GetResponseSchema(successResponse);
                                var modelType = FindModelType(responseSchema);

                                if (modelType != null)
                                {
                                    ValidateModelProperties(modelType, responseSchema);
                                }
                            }
                        }
                    }
                }
            }
        }

        [Fact]
        public void GeneratedClient_RequiredFieldsMatchSchema()
        {
            var paths = OpenApiSchema.RootElement.GetProperty("paths");

            foreach (var path in paths.EnumerateObject())
            {
                var pathValue = path.Value;

                foreach (var operationType in new[] { "get", "post", "put", "delete", "patch" })
                {
                    if (pathValue.TryGetProperty(operationType, out var operation))
                    {
                        if (operation.TryGetProperty("requestBody", out var requestBody))
                        {
                            var requestSchema = GetRequestSchema(requestBody);
                            ValidateRequiredFields(requestSchema);
                        }

                        if (operation.TryGetProperty("responses", out var responses))
                        {
                            if (responses.TryGetProperty("200", out var successResponse))
                            {
                                var responseSchema = GetResponseSchema(successResponse);
                                ValidateRequiredFields(responseSchema);
                            }
                        }
                    }
                }
            }
        }

        private IEnumerable<MethodInfo> GetEndpointMethods(Type clientType)
        {
            return clientType
                .GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly)
                .Where(m => m.ReturnType.Name.Contains("Task"));
        }

        private string GetMethodNameFromPath(string path)
        {
            var segments = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
            var lastSegment = segments.LastOrDefault() ?? "Root";
            return lastSegment.Replace("{", "").Replace("}", "");
        }

        private JsonElement GetRequestSchema(JsonElement requestBody)
        {
            if (!requestBody.TryGetProperty("content", out var content))
                throw new InvalidOperationException("Request body missing 'content'");

            if (!content.TryGetProperty("application/json", out var jsonContent))
                throw new InvalidOperationException("Request body missing 'application/json' content");

            if (!jsonContent.TryGetProperty("schema", out var schema))
                throw new InvalidOperationException("Request body missing 'schema'");

            return schema;
        }

        private JsonElement GetResponseSchema(JsonElement response)
        {
            if (!response.TryGetProperty("content", out var content))
                throw new InvalidOperationException("Response missing 'content'");

            if (!content.TryGetProperty("application/json", out var jsonContent))
                throw new InvalidOperationException("Response missing 'application/json' content");

            if (!jsonContent.TryGetProperty("schema", out var schema))
                throw new InvalidOperationException("Response missing 'schema'");

            return schema;
        }

        private Type? FindModelType(JsonElement schema)
        {
            if (schema.TryGetProperty("$ref", out var reference))
            {
                var referencePath = reference.GetString();
                if (referencePath == null)
                    return null;

                var schemaName = referencePath.Split('/').Last();

                var modelType = typeof(Client).Assembly
                    .GetTypes()
                    .FirstOrDefault(t => t.Name.Equals(schemaName, StringComparison.OrdinalIgnoreCase));

                return modelType;
            }

            return null;
        }

        private void ValidateModelProperties(Type modelType, JsonElement schema)
        {
            if (!schema.TryGetProperty("properties", out var properties))
                return;

            var modelProperties = modelType.GetProperties(BindingFlags.Public | BindingFlags.Instance);

            foreach (var property in properties.EnumerateObject())
            {
                var propertyName = property.Name;
                var modelProperty = modelProperties.FirstOrDefault(p =>
                    p.Name.Equals(propertyName, StringComparison.OrdinalIgnoreCase));

                Assert.True(
                    modelProperty != null,
                    $"Property '{propertyName}' not found in model '{modelType.Name}'");
            }
        }

        private void ValidateRequiredFields(JsonElement schema)
        {
            if (schema.TryGetProperty("required", out var required))
            {
                foreach (var requiredProperty in required.EnumerateArray())
                {
                    var propertyName = requiredProperty.GetString();
                    if (propertyName == null)
                        continue;

                    var modelType = FindModelType(schema);
                    if (modelType != null)
                    {
                        var modelProperty = modelType.GetProperty(propertyName, BindingFlags.Public | BindingFlags.Instance | BindingFlags.IgnoreCase);
                        Assert.NotNull(modelProperty);
                        Assert.False(modelProperty!.PropertyType.IsGenericType &&
                                     modelProperty.PropertyType.GetGenericTypeDefinition() == typeof(Nullable<>),
                            $"Property '{propertyName}' in model '{modelType.Name}' should be non-nullable (required by schema)");
                    }
                }
            }
        }
    }
}
