# What is VSQ?
## VoiceStudio Quantum+ Design Token System

**Date:** 2025-01-28  
**Purpose:** Explanation of VSQ design token system

---

## 🎯 WHAT IS VSQ?

**VSQ** stands for **"VoiceStudio Quantum"** - it's the prefix for all design tokens in the VoiceStudio Quantum+ application.

**VSQ** is the design system namespace that provides consistent styling values across the entire application.

---

## 📋 WHAT ARE VSQ DESIGN TOKENS?

**VSQ Design Tokens** are centralized styling values defined in `DesignTokens.xaml` that ensure:
- ✅ **Consistency** - Same values used everywhere
- ✅ **Maintainability** - Change once, update everywhere
- ✅ **Theme Support** - Easy theme switching (future)
- ✅ **Accessibility** - Support for accessibility features

---

## 🎨 VSQ TOKEN CATEGORIES

### 1. **Colors & Brushes**

**Background Colors:**
- `VSQ.Window.Background` - Main window background
- `VSQ.Panel.BackgroundBrush` - Panel background
- `VSQ.Panel.Background.DarkBrush` - Dark panel background
- `VSQ.Panel.Background.HeaderBrush` - Panel header background
- `VSQ.Panel.HeaderBackground` - Panel header background (alternative)

**Text Colors:**
- `VSQ.Text.PrimaryBrush` - Primary text color
- `VSQ.Text.SecondaryBrush` - Secondary text color
- `VSQ.Color.Text.SecondaryBrush` - Secondary text color (alternative)

**Accent Colors:**
- `VSQ.Accent.CyanBrush` - Cyan accent color
- `VSQ.Accent.LimeBrush` - Lime accent color
- `VSQ.Accent.MagentaBrush` - Magenta accent color

**Panel Colors:**
- `VSQ.Panel.BorderBrush` - Panel border color
- `VSQ.Panel.BackgroundBrush` - Panel background

**Error/Warning Colors:**
- `VSQ.Error.BackgroundBrush` - Error background
- `VSQ.Warn.BackgroundBrush` - Warning background

---

### 2. **Typography (Font Sizes)**

**Font Size Tokens:**
- `VSQ.FontSize.Caption` - Small text (captions, labels)
- `VSQ.FontSize.Body` - Body text (normal text)
- `VSQ.FontSize.Title` - Title text
- `VSQ.FontSize.Heading` - Heading text

**Text Styles:**
- `VSQ.Text.BodyStrong` - Strong body text style
- `VSQ.Text.Subtitle` - Subtitle text style
- `VSQ.Text.Title` - Title text style

---

### 3. **Spacing**

**Spacing Values:**
- `VSQ.Spacing.None` - No spacing
- `VSQ.Spacing.Value.XSmall` - Extra small spacing
- `VSQ.Spacing.Value.Small` - Small spacing
- `VSQ.Spacing.Small` - Small spacing (alternative)
- `VSQ.Spacing.Medium` - Medium spacing
- `VSQ.Spacing.Value.Medium` - Medium spacing (alternative)
- `VSQ.Spacing.Large` - Large spacing
- `VSQ.Spacing.Value.Large` - Large spacing (alternative)
- `VSQ.Spacing.Value.XLarge` - Extra large spacing

**Usage:**
- `Margin="{StaticResource VSQ.Spacing.Medium}"`
- `Padding="{StaticResource VSQ.Spacing.Value.Large},{StaticResource VSQ.Spacing.Medium}"`

---

### 4. **Sizes (Widths & Heights)**

**Control Heights:**
- `VSQ.Control.Height.Small` - Small control height
- `VSQ.Control.Height.Large` - Large control height

**Input Widths:**
- `VSQ.Input.Width.Standard` - Standard input width
- `VSQ.Input.Height.Tall` - Tall input height

**Icon Sizes:**
- `VSQ.Icon.Size.Small` - Small icon size (16px)
- `VSQ.Icon.Size.Medium` - Medium icon size (20-24px)
- `VSQ.Icon.Size.Large` - Large icon size

---

### 5. **Corner Radius**

**Corner Radius Values:**
- `VSQ.CornerRadius.Panel` - Panel corner radius
- `VSQ.CornerRadius.Button` - Button corner radius
- `VSQ.CornerRadius.Small` - Small corner radius

**Usage:**
- `CornerRadius="{StaticResource VSQ.CornerRadius.Button}"`

---

### 6. **Animations**

**Animation Durations:**
- `VSQ.Animation.Duration.Fast` - Fast animation duration
- `VSQ.Animation.Duration.Medium` - Medium animation duration

---

### 7. **Button Styles**

**Button Styles:**
- `VSQ.Button.FocusStyle` - Button focus style
- `VSQ.Button.Primary` - Primary button style

---

### 8. **Progress & Loading**

**Progress Styles:**
- `VSQ.ProgressBar.Style` - Progress bar style
- `VSQ.Loading.*` - Loading state brushes and styles

---

## 📍 WHERE ARE VSQ TOKENS DEFINED?

**File Location:**
- `src/VoiceStudio.App/Resources/DesignTokens.xaml`

**How They're Used:**
- Merged into `App.xaml` as a resource dictionary
- Available throughout the entire application
- Referenced using `{StaticResource VSQ.*}` syntax

---

## 💡 HOW TO USE VSQ TOKENS

### Example 1: Font Size
```xml
<!-- ❌ WRONG - Hardcoded -->
<TextBlock FontSize="12" Text="Hello" />

<!-- ✅ CORRECT - Design Token -->
<TextBlock FontSize="{StaticResource VSQ.FontSize.Body}" Text="Hello" />
```

### Example 2: Spacing
```xml
<!-- ❌ WRONG - Hardcoded -->
<StackPanel Margin="0,0,16,0" />

<!-- ✅ CORRECT - Design Token -->
<StackPanel Margin="0,0,{StaticResource VSQ.Spacing.Value.Large},0" />
```

### Example 3: Colors
```xml
<!-- ❌ WRONG - Hardcoded -->
<Border Background="#FF1E1E1E" />

<!-- ✅ CORRECT - Design Token -->
<Border Background="{StaticResource VSQ.Panel.BackgroundBrush}" />
```

### Example 4: Icon Sizes
```xml
<!-- ❌ WRONG - Hardcoded -->
<Button Width="20" Height="20" Content="?" />

<!-- ✅ CORRECT - Design Token -->
<Button Width="{StaticResource VSQ.Icon.Size.Medium}" 
        Height="{StaticResource VSQ.Icon.Size.Medium}" 
        Content="?" />
```

---

## 🚨 CRITICAL RULES

### Rule 1: NO Hardcoded Values
- ❌ **NEVER** use hardcoded colors, fonts, or spacing
- ✅ **ALWAYS** use VSQ.* design tokens

### Rule 2: Consistency
- ✅ All panels must use the same VSQ tokens for similar elements
- ✅ All spacing must use VSQ.Spacing.* tokens
- ✅ All fonts must use VSQ.FontSize.* tokens

### Rule 3: Single Source of Truth
- ✅ All styling values come from `DesignTokens.xaml`
- ✅ Change once in DesignTokens.xaml, updates everywhere
- ✅ No duplicate definitions

---

## 🎯 WHY VSQ TOKENS ARE IMPORTANT

### 1. **Consistency**
- Same values used everywhere
- Professional, polished appearance
- No visual inconsistencies

### 2. **Maintainability**
- Change once in `DesignTokens.xaml`
- All panels update automatically
- No need to find and replace hundreds of values

### 3. **Theme Support (Future)**
- Design tokens can reference different values per theme
- Switch theme = change token values = entire app updates
- Enables light/dark/high contrast themes

### 4. **Accessibility**
- Design tokens can scale based on accessibility settings
- High DPI support built into token system
- Better support for accessibility features

### 5. **Original ChatGPT UI Specification**
- Required by original UI specification
- Non-negotiable rule from design system
- Must be enforced 100%

---

## 📊 CURRENT STATUS

**Worker 2 is currently:**
- Systematically replacing hardcoded values with VSQ.* tokens
- Progress: 26-29 panels completed, ~600+ replacements made
- Remaining: 66-87 panels, ~815 matches (many false positives)

**Compliance:**
- ✅ All completed panels verified 100% compliant
- ✅ No hardcoded values in polished panels
- ✅ All styling uses VSQ.* design tokens

---

## ✅ SUMMARY

**VSQ = VoiceStudio Quantum**

**VSQ Design Tokens:**
- Centralized styling values
- Defined in `DesignTokens.xaml`
- Used throughout the application
- Ensure consistency and maintainability

**Usage:**
- `{StaticResource VSQ.FontSize.Body}`
- `{StaticResource VSQ.Spacing.Medium}`
- `{StaticResource VSQ.Panel.BackgroundBrush}`
- `{StaticResource VSQ.Icon.Size.Medium}`

**Rule:**
- ✅ **ALWAYS** use VSQ.* tokens
- ❌ **NEVER** use hardcoded values

---

**Last Updated:** 2025-01-28  
**Status:** ✅ **EXPLANATION COMPLETE**
