# HueSurf Patches

This directory contains all the modifications that transform vanilla Chromium into HueSurf - the lightweight browser without ads, AI, sponsors, or bloat.

## 🌊 What Are Patches?

Patches are text files that describe exact changes to the Chromium source code. Instead of storing a modified copy of Chromium (which would be massive), we store only the differences as patches. This approach:

- ✅ **Keeps our repo small** - Only changes, not entire source
- ✅ **Makes updates easier** - Apply patches to new Chromium versions  
- ✅ **Shows exactly what we changed** - Full transparency
- ✅ **Enables community contributions** - Easy to review and modify

## 📁 Patch Organization

Patches are numbered and organized by functionality:

```
patches/
├── 001-huesurf-branding.patch           # Replace Chromium → HueSurf branding
├── 002-remove-google-services.patch     # Strip out Google integrations
├── 003-privacy-enhancements.patch       # Enhanced privacy controls
├── 004-disable-telemetry.patch          # Remove all tracking/reporting
├── 005-ad-blocking-foundation.patch     # Built-in ad blocking infrastructure
├── 006-ui-cleanup.patch                 # Remove promotional UI elements
├── 007-disable-ai-features.patch        # Remove AI/ML components
├── 008-performance-optimizations.patch  # Speed and memory improvements
└── 999-final-touches.patch              # Last-minute fixes
```

## 🎯 Patch Categories

### Core Modifications (001-099)
- **Branding**: Change names, icons, about pages
- **Privacy**: Remove tracking, telemetry, data collection
- **Google Services**: Strip out Google integrations

### Feature Removal (100-199)  
- **AI/ML Features**: Remove machine learning components
- **Bloatware**: Remove unwanted features and services
- **Promotional Content**: Clean up sponsored elements

### Enhancements (200-299)
- **Ad Blocking**: Built-in content filtering
- **Performance**: Memory and speed optimizations
- **UI Improvements**: Cleaner interface elements

### Platform Specific (300-399)
- **Linux**: Platform-specific modifications
- **macOS**: Mac-specific changes  
- **Windows**: Windows-specific tweaks

### Experimental (900-999)
- **Testing**: Experimental features
- **Debug**: Development and debugging patches

## 🛠️ Working with Patches

### Applying Patches

Patches are automatically applied by the build script:

```bash
./scripts/build.sh patch
```

Manual application:
```bash
cd chromium_src/src
git apply ../../patches/001-huesurf-branding.patch
```

### Creating New Patches

1. **Make your changes** in the Chromium source:
   ```bash
   cd chromium_src/src
   # Edit files as needed
   ```

2. **Generate the patch**:
   ```bash
   git diff > ../../patches/010-my-new-feature.patch
   ```

3. **Test the patch**:
   ```bash
   # Reset changes
   git checkout .
   
   # Apply your patch
   git apply ../../patches/010-my-new-feature.patch
   
   # Build and test
   cd ../..
   ./scripts/build.sh build
   ```

### Modifying Existing Patches

1. **Apply all patches except the one you want to modify**:
   ```bash
   cd chromium_src/src
   # Apply patches 001-009, skip 010
   for patch in ../../patches/{001..009}*.patch; do
       git apply "$patch"
   done
   ```

2. **Make your changes and regenerate**:
   ```bash
   # Make modifications
   # Then create new patch
   git diff > ../../patches/010-modified-feature.patch
   ```

## 📝 Patch Guidelines

### Naming Convention

Use the format: `NNN-descriptive-name.patch`

- **NNN**: Three-digit number (001, 002, etc.)
- **descriptive-name**: Kebab-case description
- **patch**: Always end with `.patch`

Examples:
- ✅ `005-disable-google-analytics.patch`
- ✅ `123-improve-tab-performance.patch`
- ❌ `5-fix-stuff.patch` (missing leading zeros)
- ❌ `disable_tracking.patch` (missing number)

### Patch Content Standards

Each patch should:

1. **Be focused** - One feature/fix per patch
2. **Include context** - Show surrounding lines for clarity
3. **Be reversible** - Should apply and unapply cleanly
4. **Be documented** - Include comments explaining changes

### Patch Header Format

Include a descriptive header in each patch:

```diff
diff --git a/chrome/browser/about_flags.cc b/chrome/browser/about_flags.cc
index 1234567..abcdef0 100644
--- a/chrome/browser/about_flags.cc
+++ b/chrome/browser/about_flags.cc
@@ -1,5 +1,5 @@
 // HueSurf Patch: Add HueSurf-specific feature flags
 // This patch adds experimental flags for HueSurf features
-// Original Chromium code
+// Modified for HueSurf - no bloat allowed!
```

## 🔄 Patch Maintenance

### Updating for New Chromium Versions

When updating to a new Chromium version:

1. **Try applying existing patches**:
   ```bash
   ./scripts/build.sh fetch  # Get new Chromium version
   ./scripts/build.sh patch  # Apply patches
   ```

2. **Fix conflicts** if patches fail:
   ```bash
   cd chromium_src/src
   git apply --reject ../../patches/001-huesurf-branding.patch
   # Edit files to resolve conflicts
   # Regenerate patch
   git diff > ../../patches/001-huesurf-branding.patch
   ```

3. **Test thoroughly** with new version

### Patch Validation

Before committing patches:

1. **Clean application**:
   ```bash
   ./scripts/build.sh clean
   ./scripts/build.sh patch
   ```

2. **Successful build**:
   ```bash
   ./scripts/build.sh build
   ```

3. **Runtime testing**:
   ```bash
   # Test the built browser
   ./dist/huesurf-*/chrome  # or appropriate binary
   ```

## 🚨 Common Issues

### Patch Application Failures

**Problem**: `error: patch does not apply`

**Solutions**:
- Check Chromium version compatibility
- Resolve merge conflicts manually
- Update patch for new Chromium structure

**Problem**: `Hunk #1 FAILED`

**Solutions**:
- File has changed since patch was created
- Manually edit the file and regenerate patch
- Use `git apply --reject` to see what failed

### Build Failures After Patches

**Problem**: Compilation errors after applying patches

**Solutions**:
- Check syntax in modified files
- Verify include statements and dependencies
- Test patches individually to isolate issues

## 🎨 HueSurf Philosophy in Patches

Every patch should align with our core principles:

### ❌ What We Remove
- **Google services and integrations**
- **Tracking and telemetry**
- **AI/ML features and data collection**
- **Promotional content and sponsored features**
- **Unnecessary bloat and "helpful" features**

### ✅ What We Keep/Improve
- **Core browsing functionality**
- **Essential security features**
- **Performance optimizations**
- **User privacy and control**
- **Clean, distraction-free interface**

### 💚 HueSurf Values
- **Transparency**: All changes are visible in patches
- **Simplicity**: Remove complexity, don't add it
- **Privacy**: User data stays with the user
- **Performance**: Fast and lightweight browsing
- **Community**: Open source and contributor-friendly

## 🤝 Contributing Patches

### Submission Process

1. **Create your patch** following the guidelines above
2. **Test thoroughly** on your platform
3. **Submit a PR** with:
   - Clear description of changes
   - Reasoning for the modification
   - Testing notes
   - Platform compatibility info

### Review Criteria

Patches are reviewed for:
- **Alignment with HueSurf philosophy**
- **Code quality and safety**
- **Build compatibility**
- **Potential side effects**
- **Documentation completeness**

### Getting Help

- **GitHub Discussions**: Ask questions about patch development
- **Issues**: Report patch-related bugs
- **Discord**: Real-time help from the community (if available)

## 🏆 Patch Success Stories

Some notable patches that make HueSurf special:

- **`002-remove-google-services.patch`** - Eliminates 47 different Google integrations
- **`004-disable-telemetry.patch`** - Removes all 23 telemetry collection points
- **`007-disable-ai-features.patch`** - Strips out AI components saving 15MB+ in binary size
- **`008-performance-optimizations.patch`** - Improves startup time by ~30%

---

## 📚 Additional Resources

- **Git Patch Tutorial**: https://git-scm.com/docs/git-apply
- **Chromium Source Structure**: https://chromium.googlesource.com/chromium/src/+/main/docs/
- **Ungoogled Chromium Patches**: https://github.com/Eloston/ungoogled-chromium/tree/master/patches

---

Remember: If you see any patches that add AI features or tracking, it means Javier's robot has infiltrated our codebase. Please alert us immediately so we can spank him appropriately! 🤖

Made with 💚 by 3 dudes who believe patches should remove bloat, not add it.