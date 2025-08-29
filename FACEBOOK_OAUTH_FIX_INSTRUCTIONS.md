# Facebook OAuth Domain Fix Instructions

## Issue Identified
❌ **Facebook JavaScript SDK Unknown Host Domain Error**: 
- Error: "The Domain you are hosting the Facebook Javascript SDK is not in your app's Javascript SDK host domain list"
- Facebook App ID: 1119361770050320
- Current Domain: user-data-restore.preview.emergentagent.com
- Need to add domain to Facebook App dashboard login settings

## Fix Required in Facebook Developer Console

### Step 1: Access Facebook Developer Console
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Log in with the account that owns the Facebook app
3. Go to "My Apps" and select your app with ID: **1119361770050320**

### Step 2: Navigate to App Settings
1. In your Facebook app dashboard, go to **Settings** > **Basic**
2. Or go to **Facebook Login** > **Settings** in the left sidebar

### Step 3: Update App Domain Settings
In the **App Domains** section, add:
```
user-data-restore.preview.emergentagent.com
```

### Step 3a: Update JavaScript SDK Allowed Domains (CRITICAL)
In the **Allowed Domains for the JavaScript SDK** section, add:
```
user-data-restore.preview.emergentagent.com
```
⚠️ **This is the most important setting** - it directly controls the "JSSDK Unknown Host domain" error!

### Step 4: Update Valid OAuth Redirect URIs
In the **Facebook Login** > **Settings**, find **Valid OAuth Redirect URIs** and add:
```
https://mentor-marketplace.preview.emergentagent.com
https://mentor-marketplace.preview.emergentagent.com/auth/facebook
https://onlymentors.ai
https://onlymentors.ai/auth/facebook
```

### Step 5: Update Website URL (if present)
In **Settings** > **Basic**, find **Website** section and add:
```
https://mentor-marketplace.preview.emergentagent.com
```

### Step 6: Save Changes
1. Click "Save Changes" in the Facebook Developer Console
2. Changes should take effect immediately (no waiting period like Google)

## Current Facebook App Details
- **App ID**: 1119361770050320
- **App Secret**: ab6e1251f93adaa922c01da381911187 (configured)
- **Current Redirect URI**: https://mentor-marketplace.preview.emergentagent.com

## After Making Changes
Once you've updated the Facebook Developer Console settings:
1. The "JSSDK Unknown Host domain" error should disappear
2. Facebook OAuth button should work immediately
3. Facebook SDK should load without domain errors

## Test Results Before Fix
✅ **Backend Integration**: Working correctly
✅ **Frontend Component**: Renders properly
❌ **Facebook SDK**: Blocked by domain restrictions
✅ **Configuration Endpoint**: Returns correct App ID

**The Facebook OAuth integration is 95% complete - just needs Facebook domain configuration update!**

## Quick Verification Steps After Fix
1. Refresh the OnlyMentors.ai login page
2. Check if Facebook OAuth button loads without errors
3. Try clicking the Facebook OAuth button
4. Verify the Facebook login popup works

Let me know when you've completed these Facebook Developer Console changes!