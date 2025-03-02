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
```bash
# Run in terminal
az ad sp create-for-rbac --name "powerop-ml-app" --role contributor \
    --scopes /subscriptions/<subscription-id>/resourceGroups/<resource-group-name> \
    --sdk-auth
```

### Step 2: Add Secret to GitHub
1. Go to your GitHub repository
2. Click Settings → Secrets → New secret
3. Name: AZURE_CREDENTIALS
4. Value: (Paste the JSON output from previous command)

## 5. Deploying Your Application

### Using Visual Studio Code
1. Install Azure Extensions:
   - Azure Tools
   - Azure App Service
   - Azure Machine Learning

2. Deploy from VS Code:
   ```
   1. Open Command Palette (Ctrl+Shift+P)
   2. Type: Azure: Sign In
   3. Select your subscription
   4. Right-click on your project
   5. Select "Deploy to Web App"
   ```

### Using Command Line
```bash
# Deploy web app
az webapp up --sku F1 --name powerop-ml-app --resource-group powerop-ml-rg

# Deploy ML workspace
az ml workspace create --name powerop-ml-workspace \
    --resource-group powerop-ml-rg

# Create compute instance
az ml compute create --name dev-instance \
    --workspace-name powerop-ml-workspace \
    --resource-group powerop-ml-rg \
    --size STANDARD_DS11_V2 \
    --type AmlCompute
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
