# 🔧 GitHub Environments Setup Guide

## 📋 Setting Up 'production' Environment for Azure Deployment

I see your GitHub Actions workflow is failing because it's looking for an environment called 'production'. Let's create and configure it:

### Step 1: Create the Production Environment

1. In your GitHub repository, click on **Settings** tab
2. In the left sidebar, click on **Environments**
3. Click **New environment**
4. Name it exactly: `production` (must match what's in the workflow file)
5. Click **Configure environment**

### Step 2: Add Environment Secrets

Add these secrets to the production environment:

| Secret Name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | *Paste the entire contents of github-azure-credentials.json here* |

### Step 3: Configure Environment Protection Rules (Optional)

For better security, you may want to:

1. Enable **Required reviewers** and add yourself
2. Set **Wait timer** to 0 minutes
3. Enable **Deployment branches** and restrict to specific branches (main, website-plan)

### Step 4: Re-run the GitHub Actions Workflow

After setting up the environment:

1. Go to the **Actions** tab
2. Find the failed workflow run
3. Click **Re-run all jobs**

## 📋 Setting Up 'staging' Environment (Optional)

If you want to use staging for testing:

1. Create another environment named `staging`
2. Add the same secrets as production
3. You can trigger staging deployments by manually running the workflow and selecting 'staging' from the dropdown

## 🔒 About the Azure Credentials Secret

The `AZURE_CREDENTIALS` secret contains service principal credentials that GitHub Actions uses to authenticate with Azure. It should be formatted as a JSON object:

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

This is the content from the `github-azure-credentials.json` file we generated earlier.

## 🚀 After Setting Up Environments

Once environments are configured:

1. GitHub Actions will use the correct secrets for each environment
2. You can see deployment history for each environment
3. You can enforce approval requirements before deployment
4. You can restrict which branches can deploy to which environments
