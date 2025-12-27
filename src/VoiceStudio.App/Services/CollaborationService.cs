using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace VoiceStudio.App.Services
{
    /// <summary>
    /// Service for managing real-time collaboration indicators.
    /// Implements IDEA 25: Real-Time Collaboration Indicators.
    /// </summary>
    public class CollaborationService
    {
        private readonly ObservableCollection<ActiveUser> _activeUsers = new();
        private readonly Dictionary<string, UserCursor> _userCursors = new();
        private readonly Dictionary<string, UserSelection> _userSelections = new();

        public event EventHandler<ActiveUserEventArgs>? UserJoined;
        public event EventHandler<ActiveUserEventArgs>? UserLeft;
        public event EventHandler<UserCursorEventArgs>? CursorMoved;
        public event EventHandler<UserSelectionEventArgs>? SelectionChanged;

        public ObservableCollection<ActiveUser> ActiveUsers => _activeUsers;

        /// <summary>
        /// Adds or updates an active user.
        /// </summary>
        public void AddOrUpdateUser(string userId, string userName, string? avatarUrl = null, string? color = null)
        {
            var existingUser = _activeUsers.FirstOrDefault(u => u.UserId == userId);
            if (existingUser != null)
            {
                existingUser.UserName = userName;
                existingUser.AvatarUrl = avatarUrl;
                existingUser.Color = color ?? GenerateUserColor(userId);
                existingUser.LastSeen = DateTime.UtcNow;
            }
            else
            {
                var newUser = new ActiveUser
                {
                    UserId = userId,
                    UserName = userName,
                    AvatarUrl = avatarUrl,
                    Color = color ?? GenerateUserColor(userId),
                    JoinedAt = DateTime.UtcNow,
                    LastSeen = DateTime.UtcNow
                };
                _activeUsers.Add(newUser);
                UserJoined?.Invoke(this, new ActiveUserEventArgs(newUser));
            }
        }

        /// <summary>
        /// Removes an active user.
        /// </summary>
        public void RemoveUser(string userId)
        {
            var user = _activeUsers.FirstOrDefault(u => u.UserId == userId);
            if (user != null)
            {
                _activeUsers.Remove(user);
                _userCursors.Remove(userId);
                _userSelections.Remove(userId);
                UserLeft?.Invoke(this, new ActiveUserEventArgs(user));
            }
        }

        /// <summary>
        /// Updates a user's cursor position.
        /// </summary>
        public void UpdateCursor(string userId, double x, double y, string? panelId = null)
        {
            if (!_userCursors.ContainsKey(userId))
            {
                var user = _activeUsers.FirstOrDefault(u => u.UserId == userId);
                if (user == null)
                    return;

                _userCursors[userId] = new UserCursor
                {
                    UserId = userId,
                    UserName = user.UserName,
                    Color = user.Color,
                    X = x,
                    Y = y,
                    PanelId = panelId
                };
            }
            else
            {
                _userCursors[userId].X = x;
                _userCursors[userId].Y = y;
                _userCursors[userId].PanelId = panelId;
                _userCursors[userId].LastUpdated = DateTime.UtcNow;
            }

            CursorMoved?.Invoke(this, new UserCursorEventArgs(_userCursors[userId]));
        }

        /// <summary>
        /// Updates a user's selection.
        /// </summary>
        public void UpdateSelection(string userId, string selectionType, object? selectionData = null, string? panelId = null)
        {
            if (!_userSelections.ContainsKey(userId))
            {
                var user = _activeUsers.FirstOrDefault(u => u.UserId == userId);
                if (user == null)
                    return;

                _userSelections[userId] = new UserSelection
                {
                    UserId = userId,
                    UserName = user.UserName,
                    Color = user.Color,
                    SelectionType = selectionType,
                    SelectionData = selectionData,
                    PanelId = panelId
                };
            }
            else
            {
                _userSelections[userId].SelectionType = selectionType;
                _userSelections[userId].SelectionData = selectionData;
                _userSelections[userId].PanelId = panelId;
                _userSelections[userId].LastUpdated = DateTime.UtcNow;
            }

            SelectionChanged?.Invoke(this, new UserSelectionEventArgs(_userSelections[userId]));
        }

        /// <summary>
        /// Gets all user cursors for a specific panel.
        /// </summary>
        public IEnumerable<UserCursor> GetCursorsForPanel(string panelId)
        {
            return _userCursors.Values.Where(c => c.PanelId == panelId);
        }

        /// <summary>
        /// Gets all user selections for a specific panel.
        /// </summary>
        public IEnumerable<UserSelection> GetSelectionsForPanel(string panelId)
        {
            return _userSelections.Values.Where(s => s.PanelId == panelId);
        }

        /// <summary>
        /// Generates a consistent color for a user based on their ID.
        /// </summary>
        private string GenerateUserColor(string userId)
        {
            var hash = userId.GetHashCode();
            var colors = new[]
            {
                "#FF00FF00", // Green
                "#FF00FFFF", // Cyan
                "#FFFF00FF", // Magenta
                "#FFFFFF00", // Yellow
                "#FFFF8000", // Orange
                "#FF0080FF", // Blue
                "#FFFF0080", // Pink
                "#FF80FF00"  // Lime
            };
            return colors[Math.Abs(hash) % colors.Length];
        }
    }

    /// <summary>
    /// Represents an active user in the collaboration session.
    /// </summary>
    public class ActiveUser
    {
        public string UserId { get; set; } = string.Empty;
        public string UserName { get; set; } = string.Empty;
        public string? AvatarUrl { get; set; }
        public string Color { get; set; } = "#FF00FF00";
        public DateTime JoinedAt { get; set; }
        public DateTime LastSeen { get; set; }
    }

    /// <summary>
    /// Represents a user's cursor position.
    /// </summary>
    public class UserCursor
    {
        public string UserId { get; set; } = string.Empty;
        public string UserName { get; set; } = string.Empty;
        public string Color { get; set; } = "#FF00FF00";
        public double X { get; set; }
        public double Y { get; set; }
        public string? PanelId { get; set; }
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Represents a user's selection.
    /// </summary>
    public class UserSelection
    {
        public string UserId { get; set; } = string.Empty;
        public string UserName { get; set; } = string.Empty;
        public string Color { get; set; } = "#FF00FF00";
        public string SelectionType { get; set; } = string.Empty; // "clip", "track", "profile", etc.
        public object? SelectionData { get; set; }
        public string? PanelId { get; set; }
        public DateTime LastUpdated { get; set; } = DateTime.UtcNow;
    }

    /// <summary>
    /// Event arguments for active user events.
    /// </summary>
    public class ActiveUserEventArgs : EventArgs
    {
        public ActiveUser User { get; }

        public ActiveUserEventArgs(ActiveUser user)
        {
            User = user;
        }
    }

    /// <summary>
    /// Event arguments for cursor movement events.
    /// </summary>
    public class UserCursorEventArgs : EventArgs
    {
        public UserCursor Cursor { get; }

        public UserCursorEventArgs(UserCursor cursor)
        {
            Cursor = cursor;
        }
    }

    /// <summary>
    /// Event arguments for selection change events.
    /// </summary>
    public class UserSelectionEventArgs : EventArgs
    {
        public UserSelection Selection { get; }

        public UserSelectionEventArgs(UserSelection selection)
        {
            Selection = selection;
        }
    }
}

