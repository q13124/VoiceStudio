// Phase 2 Gap Fix: Unified AuthService Facade
// Provides a unified interface for authentication and authorization

using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VoiceStudio.App.Services;

/// <summary>
/// User roles matching backend UserRole enum.
/// </summary>
public enum UserRole
{
    Guest,
    User,
    Admin,
    Service
}

/// <summary>
/// Permissions matching backend Permission enum.
/// </summary>
public enum Permission
{
    Read,
    Write,
    Delete,
    Admin,
    ManageUsers,
    ManageEngines,
    ManageSettings,
    ExportData,
    ImportData,
    TrainModels
}

/// <summary>
/// Represents an authenticated user.
/// </summary>
public class AuthenticatedUser
{
    public string UserId { get; init; } = string.Empty;
    public string Username { get; init; } = string.Empty;
    public UserRole Role { get; init; } = UserRole.Guest;
    public IReadOnlyList<Permission> Permissions { get; init; } = Array.Empty<Permission>();
    public DateTime? TokenExpiry { get; init; }
    public bool IsLocalUser { get; init; }

    /// <summary>
    /// Checks if the user has a specific permission.
    /// </summary>
    public bool HasPermission(Permission permission)
    {
        // Admin has all permissions
        if (Role == UserRole.Admin)
            return true;

        return Permissions.Contains(permission);
    }

    /// <summary>
    /// Checks if the user has at least the specified role level.
    /// </summary>
    public bool HasRole(UserRole requiredRole)
    {
        var roleHierarchy = new Dictionary<UserRole, int>
        {
            { UserRole.Guest, 1 },
            { UserRole.User, 2 },
            { UserRole.Service, 2 },
            { UserRole.Admin, 3 }
        };

        return roleHierarchy.GetValueOrDefault(Role, 0) >= roleHierarchy.GetValueOrDefault(requiredRole, 0);
    }
}

/// <summary>
/// Authentication result from login operations.
/// </summary>
public class AuthResult
{
    public bool Success { get; init; }
    public AuthenticatedUser? User { get; init; }
    public string? Token { get; init; }
    public string? RefreshToken { get; init; }
    public string? ErrorMessage { get; init; }
    public DateTime? ExpiresAt { get; init; }
}

/// <summary>
/// Authentication state changed event args.
/// </summary>
public class AuthStateChangedEventArgs : EventArgs
{
    public AuthenticatedUser? PreviousUser { get; init; }
    public AuthenticatedUser? CurrentUser { get; init; }
    public bool IsAuthenticated => CurrentUser != null;
}

/// <summary>
/// Phase 2 Gap Fix: Unified authentication service interface.
/// Provides a consistent facade for all authentication operations.
/// </summary>
public interface IUnifiedAuthService
{
    #region Properties

    /// <summary>
    /// Gets the currently authenticated user, or null if not authenticated.
    /// </summary>
    AuthenticatedUser? CurrentUser { get; }

    /// <summary>
    /// Gets whether a user is currently authenticated.
    /// </summary>
    bool IsAuthenticated { get; }

    /// <summary>
    /// Gets whether authentication is required for the current environment.
    /// Local desktop mode typically doesn't require authentication.
    /// </summary>
    bool IsAuthRequired { get; }

    /// <summary>
    /// Gets whether the current session is a local user session.
    /// </summary>
    bool IsLocalSession { get; }

    #endregion

    #region Authentication Methods

    /// <summary>
    /// Initialize the authentication service and restore any existing session.
    /// </summary>
    Task InitializeAsync();

    /// <summary>
    /// Authenticate using username and password.
    /// </summary>
    Task<AuthResult> LoginAsync(string username, string password);

    /// <summary>
    /// Authenticate using an API key.
    /// </summary>
    Task<AuthResult> LoginWithApiKeyAsync(string apiKey);

    /// <summary>
    /// Log out the current user.
    /// </summary>
    Task LogoutAsync();

    /// <summary>
    /// Refresh the current authentication token.
    /// </summary>
    Task<AuthResult> RefreshTokenAsync();

    /// <summary>
    /// Create a local user session (for local desktop mode).
    /// </summary>
    Task<AuthResult> CreateLocalSessionAsync();

    #endregion

    #region Authorization Methods

    /// <summary>
    /// Check if the current user has a specific permission.
    /// </summary>
    bool HasPermission(Permission permission);

    /// <summary>
    /// Check if the current user has at least the specified role.
    /// </summary>
    bool HasRole(UserRole role);

    /// <summary>
    /// Require a specific permission, throwing if not authorized.
    /// </summary>
    void RequirePermission(Permission permission);

    /// <summary>
    /// Require a specific role, throwing if not authorized.
    /// </summary>
    void RequireRole(UserRole role);

    #endregion

    #region Token Management

    /// <summary>
    /// Get the current authentication token for API requests.
    /// </summary>
    string? GetCurrentToken();

    /// <summary>
    /// Get the current API key for API requests.
    /// </summary>
    string? GetCurrentApiKey();

    /// <summary>
    /// Check if the current token is expired or will expire soon.
    /// </summary>
    bool IsTokenExpiringSoon(TimeSpan threshold);

    #endregion

    #region Events

    /// <summary>
    /// Raised when authentication state changes.
    /// </summary>
    event EventHandler<AuthStateChangedEventArgs>? AuthStateChanged;

    #endregion
}

/// <summary>
/// Exception thrown when authentication is required but missing.
/// </summary>
public class AuthenticationRequiredException : Exception
{
    public AuthenticationRequiredException() : base("Authentication is required for this operation.") { }
    public AuthenticationRequiredException(string message) : base(message) { }
}

/// <summary>
/// Exception thrown when authorization fails.
/// </summary>
public class AuthorizationException : Exception
{
    public Permission? RequiredPermission { get; init; }
    public UserRole? RequiredRole { get; init; }

    public AuthorizationException(string message) : base(message) { }

    public AuthorizationException(Permission permission)
        : base($"Permission denied: {permission}")
    {
        RequiredPermission = permission;
    }

    public AuthorizationException(UserRole role)
        : base($"Role denied: requires {role}")
    {
        RequiredRole = role;
    }
}
