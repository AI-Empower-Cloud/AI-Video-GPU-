#!/bin/bash

# 🔐 Create Azure Service Principal for GitHub Actions
# This script creates a service principal for GitHub Actions to deploy to Azure

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       🔐 GitHub Actions - Azure Authentication Setup          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if logged in to Azure
check_login() {
    print_status "Checking Azure login status..."
    
    if ! az account show &> /dev/null; then
        print_error "Not logged in to Azure. Please login first."
        az login --use-device-code
    else
        ACCOUNT_INFO=$(az account show --output tsv --query '[name,user.name]')
        print_success "Already logged into Azure"
        echo "   Account: $(echo $ACCOUNT_INFO | cut -f1)"
        echo "   User: $(echo $ACCOUNT_INFO | cut -f2)"
    fi
}

# Create service principal
create_service_principal() {
    print_status "Creating Azure service principal for GitHub Actions..."
    
    # Get subscription ID
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    print_status "Using subscription: $SUBSCRIPTION_ID"
    
    # Create a resource group if it doesn't exist
    RG_NAME="ai-gpu-studio-rg"
    if ! az group show --name $RG_NAME &> /dev/null; then
        print_status "Creating resource group: $RG_NAME"
        az group create --name $RG_NAME --location eastus --output none
    else
        print_status "Using existing resource group: $RG_NAME"
    fi
    
    # Create service principal with Contributor role
    print_status "Creating service principal with Contributor access..."
    SP_NAME="github-actions-ai-gpu-studio"
    
    # Check if service principal exists
    if az ad sp list --filter "displayName eq '${SP_NAME}'" --query "[].displayName" -o tsv | grep -q "$SP_NAME"; then
        print_status "Service principal already exists. Recreating it..."
        SP_ID=$(az ad sp list --filter "displayName eq '${SP_NAME}'" --query "[].id" -o tsv)
        az ad sp delete --id $SP_ID
    fi
    
    # Create new service principal and assign role
    JSON=$(az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role "Contributor" \
        --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG_NAME" \
        --sdk-auth \
        --output json)
    
    # Format JSON for GitHub secrets
    echo "$JSON" > github-azure-credentials.json
    
    # Print success message
    print_success "Service principal created successfully!"
    echo ""
    echo "🔑 GitHub Actions Credentials saved to: github-azure-credentials.json"
    echo ""
    echo "📋 Next steps:"
    echo "1. Add this secret to GitHub:"
    echo "   - Go to your repository on GitHub"
    echo "   - Click 'Settings' → 'Secrets and variables' → 'Actions'"
    echo "   - Click 'New repository secret'"
    echo "   - Name: AZURE_CREDENTIALS"
    echo "   - Value: Copy and paste the entire contents of github-azure-credentials.json"
    echo ""
    echo "2. Re-run the GitHub Actions workflow"
    echo ""
}

# Main function
main() {
    print_header
    
    echo "This script will create an Azure service principal with Contributor"
    echo "permissions for GitHub Actions to deploy to Azure."
    echo ""
    echo "Requirements:"
    echo "- Azure CLI installed"
    echo "- Logged in to Azure"
    echo ""
    
    read -p "Continue? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        echo "Setup canceled."
        exit 0
    fi
    
    # Check login status
    check_login
    
    # Create service principal
    create_service_principal
}

# Run main function
main
