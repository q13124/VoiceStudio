# Build the unified installer (Burn)
1) Build MSIs:
   - `Installer\VoiceStudio.Installer\build.ps1`
   - `Installer\VoiceStudio.ContentInstaller\build.ps1`
2) (Optional) Drop prereqs into `Installer\3rdparty\`:
   - VC_redist.x64.exe
   - ffmpeg-setup.exe (silent)
3) Build bundle:
   - `Installer\VoiceStudio.Bootstrapper\build.ps1`
Result: `out\bundle\VoiceStudioSetup.exe`
