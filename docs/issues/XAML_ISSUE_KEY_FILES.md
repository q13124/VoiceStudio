# VoiceStudio XAML Compilation Issue - Key Project Files

**Date**: 2026-02-01
**Issue**: WinUI 3 unpackaged app builds successfully but crashes at startup due to ResourceDictionary loading failures.

---

## Problem Summary

```
CRASH: 0xc000027b (STATUS_STOWED_EXCEPTION) in Microsoft.UI.Xaml.dll
CAUSE: ResourceDictionary files use ms-appx:/// URIs but aren't in .pri package resources

CATCH-22:
- Can't compile as <Page>: XAML compiler fails on cross-dictionary StaticResource refs
- Can't use as <Content>: ms-appx:/// URIs don't work for loose files
- Adding x:Class + code-behind: Same failure - compiler can't resolve cross-dictionary refs

SDK VERSION: Microsoft.WindowsAppSDK 1.8.251106002
TARGET: net8.0-windows10.0.19041.0, unpackaged deployment
```

---

## File 1: VoiceStudio.App.csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <!-- XAML bypass targets are imported via Directory.Build.targets (after NuGet) -->
  <!-- Do NOT import here - it must be AFTER NuGet package targets -->

  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0-windows10.0.19041.0</TargetFramework>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <GenerateTargetFrameworkAttribute>false</GenerateTargetFrameworkAttribute>
    <RootNamespace>VoiceStudio.App</RootNamespace>
    <ApplicationManifest>app.manifest</ApplicationManifest>
    <Nullable>enable</Nullable>
    <UseWinUI>true</UseWinUI>
    <TargetPlatformMinVersion>10.0.17763.0</TargetPlatformMinVersion>
    <!-- Ensure WinRT.Runtime reference assemblies are available to XAML compiler. -->
    <WindowsSdkPackageVersion>10.0.26100.81</WindowsSdkPackageVersion>
    <Platform>x64</Platform>
    <Platforms>x64</Platforms>
    <PlatformTarget>x64</PlatformTarget>
    <IsPackable>false</IsPackable>
    <GeneratePackageOnBuild>false</GeneratePackageOnBuild>
    <!-- Use system-installed Windows App SDK runtime (unpackaged app via Bootstrap.Initialize). -->
    <WindowsAppSDKSelfContained>false</WindowsAppSDKSelfContained>
    <SelfContained>true</SelfContained>
    <UseAppHost>true</UseAppHost>
    <!-- Don't set RuntimeIdentifier explicitly - let the EnsureRuntimeIdentifierForWin2D target
    handle it -->
    <!-- Setting RuntimeIdentifier causes RID-specific output paths which break the XAML compiler
    Exec task with double backslashes -->
    <!-- <RuntimeIdentifier>win-x64</RuntimeIdentifier> -->
    <!-- <RuntimeIdentifiers>win-x64</RuntimeIdentifiers> -->
    <!-- Suppress RuntimeIdentifier errors for unsupported RIDs -->
    <_SuppressWinRTError>true</_SuppressWinRTError>
    <!-- Allow RID resolution for Win2D, but suppress other RID errors -->
    <EnableDefaultRuntimeIdentifier>true</EnableDefaultRuntimeIdentifier>
    <!-- Avoid VC/meta-dependent Win32 codegen in XAML compiler -->
    <EnableWin32Codegen>false</EnableWin32Codegen>
    <UseVCMetaManaged>false</UseVCMetaManaged>
    <!-- Legacy workaround (can be revisited once XAML pipeline is stable) -->
    <!-- <DisableXbfGeneration>true</DisableXbfGeneration> -->
    <!-- <EnableUIXamlCompilation>false</EnableUIXamlCompilation> -->
    <!-- VS-0035 fix: Force external XamlCompiler via wrapper to avoid WMC9999 in-process failures. -->
    <UseXamlCompilerExecutable>false</UseXamlCompilerExecutable>
    <CppWinRTFastAbi>false</CppWinRTFastAbi>
    <BaseOutputPath>$(SolutionDir).buildlogs\</BaseOutputPath>
    <!-- FIX: Don't use architecture-specific sub-paths that cause double backslash in XAML compiler
    Exec command -->
    <!-- Set a simple flat structure for intermediate output to avoid the escaping issue -->
    <IntermediateOutputPathHasTrailingSlash>false</IntermediateOutputPathHasTrailingSlash>
    <EnforceCodeStyleInBuild>True</EnforceCodeStyleInBuild>
    <Win2DWarnNoPlatform>true</Win2DWarnNoPlatform>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
    <DefineConstants>$(DefineConstants);DISABLE_XAML_GENERATED_MAIN</DefineConstants>
  </PropertyGroup>

  <PropertyGroup>
    <!-- Unpackaged apphost EXE defaults -->
    <WindowsPackageType>None</WindowsPackageType>
    <EnableMsixTooling>false</EnableMsixTooling>
    <EnableDefaultPriItems>false</EnableDefaultPriItems>
    <GenerateAppxPackageOnBuild>false</GenerateAppxPackageOnBuild>
    <AppxPackageDir />
    <AppxBundle>Never</AppxBundle>
    <AppxManifest />
  </PropertyGroup>

  <!-- ... package references omitted for brevity ... -->

  <!-- Ensure control XAMLs carry Page metadata -->
  <ItemGroup>
    <Page Update="Controls\**\*.xaml">
      <Generator>MSBuild:Compile</Generator>
      <SubType>Designer</SubType>
    </Page>
  </ItemGroup>

  <!-- ResourceDictionary files WITH x:Class and code-behind are now compiled as Pages.
       Only files without code-behind remain excluded. -->
  <ItemGroup>
    <!-- These files have code-behind and can be compiled as Pages -->
    <Page Update="Resources\Styles\Controls.xaml">
      <Generator>MSBuild:Compile</Generator>
      <SubType>Designer</SubType>
    </Page>
    <Page Update="Resources\Styles\Text.xaml">
      <Generator>MSBuild:Compile</Generator>
      <SubType>Designer</SubType>
    </Page>
    <Page Update="Resources\Styles\Panels.xaml">
      <Generator>MSBuild:Compile</Generator>
      <SubType>Designer</SubType>
    </Page>
    <Page Update="Resources\DesignTokens.xaml">
      <Generator>MSBuild:Compile</Generator>
      <SubType>Designer</SubType>
    </Page>
    <!-- Files without code-behind remain as Content -->
    <Page Remove="Resources\Styles\EmptyStateStyles.xaml" />
    <Page Remove="Resources\Styles\LoadingSkeletonStyles.xaml" />
    <Page Remove="Resources\Styles\ToastStyles.xaml" />
    <Page Remove="Resources\Density.*.xaml" />
    <Page Remove="Resources\Theme.*.xaml" />
    <Page Remove="Resources\PanelTemplates.xaml" />
    <Content Include="Resources\Styles\EmptyStateStyles.xaml">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
    <!-- ... more Content items ... -->
  </ItemGroup>

  <ItemGroup>
    <PRIResource Include="Resources\Resources.resw" />
    <PRIResource Include="Resources\en-US\Resources.resw" />
  </ItemGroup>

</Project>
```

---

## File 2: App.xaml (loads the ResourceDictionaries)

```xml
<Application x:Class="VoiceStudio.App.App"
  xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Application.Resources>
    <ResourceDictionary>
      <ResourceDictionary.MergedDictionaries>
        <!-- WinUI default styles (DefaultButtonStyle/DefaultProgressRingStyle/etc). Required for VSQ.* styles that are BasedOn defaults. -->
        <XamlControlsResources xmlns="using:Microsoft.UI.Xaml.Controls" />
        <!-- Design tokens (VSQ.*) -->
        <ResourceDictionary Source="ms-appx:///Resources/DesignTokens.xaml" />
        <!-- Style dictionaries -->
        <ResourceDictionary Source="ms-appx:///Resources/Styles/Controls.xaml" />
        <ResourceDictionary Source="ms-appx:///Resources/Styles/Text.xaml" />
        <ResourceDictionary Source="ms-appx:///Resources/Styles/Panels.xaml" />
      </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
  </Application.Resources>
</Application>
```

---

## File 3: Controls.xaml (THE PROBLEMATIC FILE)

This file uses `{StaticResource}` references to resources defined in `DesignTokens.xaml`:

```xml
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <!-- Progress + loading -->
    <Style x:Key="VSQ.LoadingSpinner.Style" TargetType="ProgressRing">
        <Setter Property="Width" Value="{StaticResource VSQ.Icon.Size.Large}" />
        <Setter Property="Height" Value="{StaticResource VSQ.Icon.Size.Large}" />
        <Setter Property="Foreground" Value="{StaticResource VSQ.Loading.ForegroundBrush}" />
        <Setter Property="IsActive" Value="True" />
    </Style>
    <Style x:Key="VSQ.ProgressBar.Style" TargetType="ProgressBar">
        <Setter Property="Foreground" Value="{StaticResource VSQ.Progress.ForegroundBrush}" />
    </Style>

    <!-- Basic button styles (no triggers/templates; WinUI-safe) -->
    <Style x:Key="VSQ.Button.Primary" TargetType="Button">
        <Setter Property="Background" Value="{StaticResource VSQ.Accent.CyanBrush}" />
        <Setter Property="Foreground" Value="{StaticResource VSQ.Text.PrimaryBrush}" />
        <Setter Property="CornerRadius" Value="{StaticResource VSQ.CornerRadius.Button}" />
        <Setter Property="Padding" Value="{StaticResource VSQ.Spacing.Medium}" />
    </Style>
    
    <!-- ... more styles using StaticResource from DesignTokens.xaml ... -->
    
    <!-- Navigation rail toggle button with ControlTemplate -->
    <Style x:Key="VSQ.Button.NavToggle" TargetType="ToggleButton">
        <Setter Property="MinWidth" Value="{StaticResource VSQ.Control.Width.Large}" />
        <Setter Property="MinHeight" Value="{StaticResource VSQ.Control.Height.Large}" />
        <!-- ... -->
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="ToggleButton">
                    <Grid>
                        <Border x:Name="NavBorder"
                                Background="{TemplateBinding Background}"
                                BorderBrush="{TemplateBinding BorderBrush}"
                                BorderThickness="{TemplateBinding BorderThickness}"
                                CornerRadius="{TemplateBinding CornerRadius}">
                            <!-- ... -->
                        </Border>
                    </Grid>
                    <VisualStateManager.VisualStateGroups>
                        <VisualStateGroup x:Name="CommonStates">
                            <VisualState x:Name="PointerOver">
                                <Storyboard>
                                    <ObjectAnimationUsingKeyFrames Storyboard.TargetName="NavBorder"
                                                                   Storyboard.TargetProperty="Background">
                                        <DiscreteObjectKeyFrame KeyTime="0" Value="{StaticResource VSQ.Panel.Background.DarkerBrush}" />
                                    </ObjectAnimationUsingKeyFrames>
                                    <!-- ... more StaticResource refs ... -->
                                </Storyboard>
                            </VisualState>
                            <!-- ... -->
                        </VisualStateGroup>
                    </VisualStateManager.VisualStateGroups>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>
</ResourceDictionary>
```

---

## File 4: DesignTokens.xaml (defines the resources that Controls.xaml references)

```xml
<ResourceDictionary x:Class="VoiceStudio.App.Resources.DesignTokens"
  xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <!-- Brushes (WinUI 3 compatible - using hex colors directly) -->
  <SolidColorBrush x:Key="VSQ.Background.Darker" Color="#FF0A0F15" />
  <SolidColorBrush x:Key="VSQ.Background.Dark" Color="#FF121A24" />
  <SolidColorBrush x:Key="VSQ.Accent.Cyan" Color="#FF00B7C2" />
  <SolidColorBrush x:Key="VSQ.Text.PrimaryBrush" Color="#FFCDD9E5" />
  <SolidColorBrush x:Key="VSQ.Text.SecondaryBrush" Color="#FF8A9BB3" />
  <SolidColorBrush x:Key="VSQ.Text.OnAccentBrush" Color="#FF0A0F15" />
  <SolidColorBrush x:Key="VSQ.Accent.CyanBrush" Color="#FF00B7C2" />
  <SolidColorBrush x:Key="VSQ.Panel.BorderBrush" Color="#26FFFFFF" />
  <SolidColorBrush x:Key="VSQ.Panel.Background.DarkBrush" Color="#FF151921" />
  <SolidColorBrush x:Key="VSQ.Panel.Background.DarkerBrush" Color="#FF1E2329" />
  <SolidColorBrush x:Key="VSQ.Panel.Background.MasterBrush" Color="#FF252A34" />
  <SolidColorBrush x:Key="VSQ.Loading.ForegroundBrush" Color="#FF00B7C2" />
  <SolidColorBrush x:Key="VSQ.Progress.ForegroundBrush" Color="#FF00B7C2" />
  
  <!-- Typography sizes -->
  <x:Double x:Key="VSQ.FontSize.Body">12</x:Double>
  <x:Double x:Key="VSQ.Icon.Size.Large">32</x:Double>
  
  <!-- Control sizes -->
  <x:Double x:Key="VSQ.Control.Width.Medium">32</x:Double>
  <x:Double x:Key="VSQ.Control.Width.Large">40</x:Double>
  <x:Double x:Key="VSQ.Control.Height.Medium">32</x:Double>
  <x:Double x:Key="VSQ.Control.Height.Large">40</x:Double>
  
  <!-- Spacing -->
  <Thickness x:Key="VSQ.Spacing.Medium">8</Thickness>
  
  <!-- Corner radius -->
  <CornerRadius x:Key="VSQ.CornerRadius.Button">4</CornerRadius>
</ResourceDictionary>
```

---

## The Core Problem

When the XAML compiler processes `Controls.xaml`:
1. It sees `{StaticResource VSQ.Accent.CyanBrush}` 
2. It tries to resolve this at compile time
3. `VSQ.Accent.CyanBrush` is defined in `DesignTokens.xaml` (a different file)
4. **XAML compiler cannot resolve cross-file StaticResource references at compile time**
5. **Compiler fails silently with exit code 1**

At runtime, merged dictionaries would resolve this correctly, but we can't get there because the build fails.
