using Windows.UI.Input;

namespace VoiceStudio.App.Utilities
{
    public static class PointerPointPropertiesExtensions
    {
        // Compatibility shims used by older code paths. Return false if platform key state APIs
        // are not available in the current execution context. These are conservative no-op
        // implementations that keep compilation working; behavior can be refined later.
        public static bool IsControlKeyPressed(this PointerPointProperties props)
        {
            return false;
        }

        public static bool IsShiftKeyPressed(this PointerPointProperties props)
        {
            return false;
        }
    }
}
