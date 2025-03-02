# Azure Login Troubleshooting Guide

## Issue: Account Access Error
If you're seeing "account does not exist in tenant" or "no subscriptions found" errors, follow these steps:

### Step 1: Verify Student Account Setup
1. Go to [Azure for Students](https://azure.microsoft.com/free/students)
2. Click "Start Free"
3. Use your student email (NOT your personal Microsoft account)
   - If using outlook.com/live.com email, this won't work
   - Must use your .edu email or school-provided email

### Step 2: Create Azure Account
1. Visit [Azure Account Create](https://signup.azure.com/studentverification)
2. Select "Verify through school"
3. Enter your student email
4. Complete academic verification

### Step 3: Fix Login Issues
```bash
# Clear existing Azure CLI credentials
az logout

# Clear Azure CLI cache (Windows)
del "%USERPROFILE%\.azure\msal_token_cache.bin"
del "%USERPROFILE%\.azure\azureProfile.json"

# Clear Azure CLI cache (Linux/Mac)
rm ~/.azure/msal_token_cache.bin
rm ~/.azure/azureProfile.json

# Login with correct account
az login --allow-no-subscriptions

# If browser login doesn't work, try device code login
az login --use-device-code
```

### Step 4: Verify Subscription
```bash
# List all subscriptions
az account list --output table

# If no subscriptions appear, visit Azure portal:
# 1. Go to https://portal.azure.com
# 2. Click on "Subscriptions"
# 3. Look for "Azure for Students"
# 4. If not found, return to Azure for Students signup
```

## Common Solutions

### If Using Personal Microsoft Account
1. Log out completely from Azure Portal
2. Clear browser cache
3. Use student email instead
4. Complete academic verification

### If Still No Access
1. Ensure student email is verified
2. Check if school is eligible for Azure for Students
3. Contact school's IT department
4. Contact Azure Support with error codes:
   - Trace ID: (from your error message)
   - Correlation ID: (from your error message)

## Next Steps After Fix
1. Verify subscription:
```bash
az account show
```

2. Set correct subscription:
```bash
az account set --subscription "Azure for Students"
```

3. Verify access:
```bash
az group list
```
