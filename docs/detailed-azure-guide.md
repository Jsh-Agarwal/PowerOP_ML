# Detailed Azure Deployment Guide for Beginners

## Prerequisites
- A student email address
- Git installed on your computer
- Visual Studio Code (recommended)
- Azure CLI installed ([Download Link](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))

## 1. Student Account Setup (With Screenshots)

### Step 1: Account Creation
1. Go to [Azure for Students](https://azure.microsoft.com/free/students)
2. Click the "Start Free" button
3. Sign in with your student email
4. You'll need to verify your student status
5. Complete the registration form (no credit card required)

### Step 2: Azure Portal Navigation
1. Visit [Azure Portal](https://portal.azure.com)
2. The dashboard will look like this:
   ```
   +------------------------+
   |  ☰ All Services       |
   |  📊 Home              |
   |  ⚡ Resources         |
   |  🔧 Settings          |
   +------------------------+
   ```

## 2. Setting Up Your Development Environment

### Install Required Tools
```bash
# Install Azure CLI
# For Windows (PowerShell as administrator):
winget install -e --id Microsoft.AzureCLI

# For macOS:
brew install azure-cli

# Login to Azure
az login

# Verify installation
az --version
```

## 3. Creating Your First Azure Resources

### Step 1: Resource Group Creation
1. In Azure Portal:
   - Click "Create a resource"
   - Search for "Resource Group"
   - Click "Create"
2. Fill in details:
   ```
   Subscription: Azure for Students
   Resource group: powerop-ml-rg
   Region: East US (or closest to you)
   ```

### Step 2: Machine Learning Workspace
1. In Azure Portal:
   - Click "Create a resource"
   - Search for "Machine Learning"
   - Select "Azure Machine Learning"
2. Basic settings:
   ```
   Workspace name: powerop-ml-workspace
   Resource group: powerop-ml-rg
   Location: East US
   ```

## 4. Setting Up GitHub Actions

### Step 1: Generate Azure Credentials
Open Azure Cloud Shell (browser-based terminal) or Windows PowerShell/Command Prompt with Azure CLI installed:

**Option 1: Azure Cloud Shell (Recommended for beginners)**
1. Go to [Azure Portal](https://portal.azure.com)
2. Click on the Cloud Shell icon (>_) in the top menu bar
3. Select PowerShell or Bash (either will work)
4. Run the following command (all in one line):
```bash
az ad sp create-for-rbac --name "powerop-ml-app" --role contributor --scopes /subscriptions/a5b55387-1733-4297-aaea-9dafbfcab6ed/resourceGroups/powerop-ml-rg --sdk-auth
```

**Option 2: Local Windows PowerShell**
1. Press Win + X and select "Windows PowerShell" or "Windows PowerShell (Admin)"
2. Ensure Azure CLI is installed by running `az --version`
3. Run `az login` first if you haven't logged in
4. Then run the same command as above

Note: The command above uses your specific subscription ID. Make sure you're in the correct subscription before running the command.

### Step 2: Add Secret to GitHub
1. Copy the entire JSON output from the previous command, which looks like:
   ```json
   {
     "clientId": "...",
     "clientSecret": "...",
     "subscriptionId": "...",
     "tenantId": "...",
     ...
   }
   ```
2. Go to your GitHub repository
3. Click Settings → Secrets and variables → Actions
4. Click "New repository secret"
5. Configure the secret:
   - Name: `AZURE_CREDENTIALS`
   - Secret: Paste the entire JSON output including the curly braces
6. Click "Add secret"

⚠️ Important: Keep this JSON secure and never share it or commit it to your repository.

## 5. Deploying Your Application

### Method 1: Using Azure Portal (Recommended)
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Web App"
4. Fill in the basics:
   ```
   Resource Group: powerop-ml-rg
   Name: powerop-ml-app
   Publish: Code
   Runtime stack: Python 3.9
   Operating System: Linux
   Region: East US
   Linux Plan: Create new
   Sku and size: F1 (Free)
   ```
5. Click "Review + create" then "Create"
6. Once created, go to your web app
7. Go to Configuration → General settings
8. Set the following:
   ```
   Startup Command: gunicorn --bind=0.0.0.0 --timeout 600 api.main:app
   ```
   Note: We changed `app:app` to `api.main:app` to match your application structure

9. Go to Configuration → Application settings
   Add these settings:
   ```
   Name: SCM_DO_BUILD_DURING_DEPLOYMENT
   Value: true
   
   Name: PYTHON_VERSION
   Value: 3.9
   ```

10. Make sure you have these files in your project:
    - requirements.txt:
    ```
    fastapi
    uvicorn
    gunicorn
    ```
    - .deployment (new file):
    ```
    [config]
    SCM_DO_BUILD_DURING_DEPLOYMENT=1
    ```

### Method 2: Using VS Code (Alternative)
1. Install required extensions:
   - Azure Account
   - Azure App Service

2. Sign in to Azure:
   - Press Ctrl+Shift+P
   - Type "Azure: Sign In"
   - Complete browser authentication

3. Open your project:
   - File → Open Folder
   - Select your project folder
   - Make sure you're in the root directory where your code is

4. Detailed deployment steps:
   a. In VS Code's Explorer (Ctrl+Shift+E):
      - Expand your project folder
      - Right-click on the folder containing your web app files
      - Look for "Deploy to Web App..." in the context menu
      ![Right-click menu](https://i.imgur.com/example1.png)

   b. If you don't see "Deploy to Web App...":
      - Press Ctrl+Shift+P
      - Type "Azure App Service: Deploy to Web App"
      - Press Enter

   c. Follow the prompts in this order:
      1. "Create new Web App"
      2. Enter a globally unique name (e.g., "powerop-ml-app")
      3. Select your subscription ("Azure for Students")
      4. Select "Python 3.9" as runtime stack
      5. Select "Linux" as operating system
      6. Select "Free F1" pricing tier
      7. Choose the same region as your resource group (East US)
      8. Wait for creation (about 2-3 minutes)
      9. When prompted about deployment, select "Deploy"
      10. When asked about build, select "Yes"

5. Monitor deployment:
   - Watch the bottom right notifications
   - Check Output panel (Ctrl+Shift+U) for deployment logs
   - Wait for "Deployment completed" message

6. Once deployed:
   - Click "Browse Website" in the success notification
   - Or find your app URL in the Azure Portal under your web app resource

### FastAPI-Specific Troubleshooting
- If app fails to start:
  1. Check Application Logs in Azure Portal
  2. Verify your entry point matches the startup command
  3. Make sure all dependencies are in requirements.txt
  
- If you get 500 errors:
  1. Check if gunicorn is in requirements.txt
  2. Verify your app variable name matches startup command
  3. Try adding these to requirements.txt:
     ```
     python-multipart
     python-dotenv
     ```

- If deployment fails:
  1. Check if .deployment file exists
  2. Verify Python version matches your local version
  3. Make sure requirements.txt is in root directory

### Troubleshooting VS Code Deployment
- If right-click doesn't show deployment options:
  1. Command Palette (Ctrl+Shift+P)
  2. Type "Azure App Service: Create New Web App"
  3. Follow the same steps as above

- If you can't find Azure menu:
  1. View → Command Palette
  2. Type "Azure: Sign In" first
  3. Then type "Azure: Show Azure Menu"
  4. Look for Azure icon in the Activity Bar (left side)

- If deployment fails:
  1. Check the Output panel
  2. Select "Azure App Service" from the dropdown
  3. Look for specific error messages

### Troubleshooting
If you see "No subscription":
```bash
az login
az account set --subscription "a5b55387-1733-4297-aaea-9dafbfcab6ed"
```

## 6. Monitoring Your Resources

### Setting Up Cost Alerts
1. Go to Cost Management + Billing
2. Click "Cost alerts"
3. Create new alert:
   ```
   Alert type: Budget
   Amount: $50
   Alert conditions: 70% of budget
   Email recipients: Your email
   ```

## 7. Common Issues and Solutions

### Error: "Subscription not found"
```bash
# Fix by selecting correct subscription
az account list
az account set --subscription <subscription-id>
```

### Error: "Resource group not found"
```bash
# Verify resource group exists
az group list
```

## 8. Best Practices

### Security
- Never commit credentials to Git
- Use environment variables
- Rotate access keys regularly

### Cost Management
- Stop compute instances when not in use
- Use free tier services when possible
- Set up budget alerts

## 9. Useful Commands Reference

```bash
# List all resources
az resource list

# Get resource details
az resource show --name <resource-name> --resource-group <resource-group>

# Delete resource
az resource delete --name <resource-name> --resource-group <resource-group>

# Get deployment logs
az webapp log tail --name powerop-ml-app --resource-group powerop-ml-rg
```

## 10. Next Steps
- Explore Azure ML Studio
- Set up monitoring and logging
- Implement CI/CD pipelines
- Learn about scaling options

Need help? Visit [Azure Student FAQ](https://azure.microsoft.com/free/students/faq/) or contact Azure Support.
