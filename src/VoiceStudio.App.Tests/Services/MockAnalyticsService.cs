using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Tests.Services
{
    /// <summary>
    /// Mock implementation of IAnalyticsService for testing.
    /// Tracks events in memory for verification in tests.
    /// </summary>
    public class MockAnalyticsService : IAnalyticsService
    {
        private readonly List<AnalyticsEvent> _events = new();
        private readonly Dictionary<string, FlowContext> _activeFlows = new();
        private readonly object _lock = new();

        public event EventHandler<AnalyticsEvent>? EventTracked;

        /// <summary>
        /// Gets all tracked events.
        /// </summary>
        public IReadOnlyList<AnalyticsEvent> Events => new ReadOnlyCollection<AnalyticsEvent>(_events.ToList());

        /// <summary>
        /// Gets all active flows.
        /// </summary>
        public IReadOnlyDictionary<string, FlowContext> ActiveFlows => 
            new ReadOnlyDictionary<string, FlowContext>(_activeFlows);

        /// <summary>
        /// Clears all tracked events and flows.
        /// </summary>
        public void Clear()
        {
            lock (_lock)
            {
                _events.Clear();
                _activeFlows.Clear();
            }
        }

        /// <summary>
        /// Gets events by name.
        /// </summary>
        public IReadOnlyList<AnalyticsEvent> GetEventsByName(string eventName)
        {
            lock (_lock)
            {
                return _events.Where(e => e.EventName == eventName).ToList().AsReadOnly();
            }
        }

        public void TrackEvent(string eventName, Dictionary<string, object>? properties = null)
        {
            var evt = new AnalyticsEvent
            {
                Timestamp = DateTime.UtcNow,
                EventName = eventName,
                Properties = properties
            };

            lock (_lock)
            {
                _events.Add(evt);
            }

            EventTracked?.Invoke(this, evt);
        }

        public string StartFlow(string flowName, Dictionary<string, object>? properties = null)
        {
            var flowId = Guid.NewGuid().ToString("N");
            var context = new FlowContext
            {
                FlowId = flowId,
                FlowName = flowName,
                StartTime = DateTime.UtcNow,
                Properties = properties ?? new Dictionary<string, object>()
            };

            lock (_lock)
            {
                _activeFlows[flowId] = context;
            }

            TrackEvent($"{flowName}_started", new Dictionary<string, object>
            {
                { "flow_id", flowId },
                { "flow_name", flowName }
            });

            return flowId;
        }

        public void EndFlow(string flowId, bool success = true, Dictionary<string, object>? properties = null)
        {
            FlowContext? context = null;
            lock (_lock)
            {
                if (_activeFlows.TryGetValue(flowId, out context))
                {
                    _activeFlows.Remove(flowId);
                }
            }

            if (context != null)
            {
                var duration = DateTime.UtcNow - context.StartTime;
                var props = new Dictionary<string, object>
                {
                    { "flow_id", flowId },
                    { "flow_name", context.FlowName },
                    { "duration_ms", duration.TotalMilliseconds },
                    { "success", success }
                };

                if (properties != null)
                {
                    foreach (var prop in properties)
                    {
                        props[prop.Key] = prop.Value;
                    }
                }

                TrackEvent($"{context.FlowName}_ended", props);
            }
        }

        public IReadOnlyList<AnalyticsEvent> GetRecentEvents(int count = 100)
        {
            lock (_lock)
            {
                return _events.TakeLast(count).ToList().AsReadOnly();
            }
        }

        /// <summary>
        /// Internal class for tracking flow context (matches AnalyticsService implementation).
        /// </summary>
        public class FlowContext
        {
            public string FlowId { get; set; } = string.Empty;
            public string FlowName { get; set; } = string.Empty;
            public DateTime StartTime { get; set; }
            public Dictionary<string, object> Properties { get; set; } = new();
        }
    }
}