#!/bin/bash

# 🌐 GitHub CLI Environment Setup Script
# This script automates the setup of GitHub Environments and secrets

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       🌐 GitHub Environments & Secrets Setup                  ║${NC}"
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

# Check if GitHub CLI is installed
check_gh_cli() {
    print_status "Checking for GitHub CLI..."
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI not found!"
        echo ""
        echo "📥 Installing GitHub CLI automatically..."
        
        # Install GitHub CLI based on OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux installation
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
            && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
            && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
            && sudo apt update \
            && sudo apt install gh -y
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS installation
            brew install gh
        else
            print_error "Unsupported OS. Please install GitHub CLI manually: https://cli.github.com/manual/installation"
            exit 1
        fi
        
        print_success "GitHub CLI installed successfully"
    else
        print_success "GitHub CLI found"
        echo "   Version: $(gh --version | head -n1)"
    fi
}

# Check GitHub login status
check_gh_login() {
    print_status "Checking GitHub authentication status..."
    
    if ! gh auth status &> /dev/null; then
        print_error "Not logged into GitHub. Please login first."
        gh auth login
    else
        ACCOUNT_INFO=$(gh auth status 2>&1 | grep "Logged in" || echo "Unknown")
        print_success "Already logged into GitHub"
        echo "   $ACCOUNT_INFO"
    fi
}

# Get repository information
get_repo_info() {
    print_status "Getting repository information..."
    
    # Try to get repo from remote origin
    REMOTE_URL=$(git config --get remote.origin.url)
    
    if [[ $REMOTE_URL == *"github.com"* ]]; then
        # Extract owner and repo from URL
        if [[ $REMOTE_URL == *"github.com:"* ]]; then
            # SSH format
            REPO_INFO=${REMOTE_URL#*github.com:}
        else
            # HTTPS format
            REPO_INFO=${REMOTE_URL#*github.com/}
        fi
        
        # Remove .git if present
        REPO_INFO=${REPO_INFO%.git}
        
        REPO_OWNER=$(echo $REPO_INFO | cut -d'/' -f1)
        REPO_NAME=$(echo $REPO_INFO | cut -d'/' -f2)
    else
        # Ask for repository info manually
        echo "Repository information could not be automatically determined."
        read -p "Enter repository owner (organization or username): " REPO_OWNER
        read -p "Enter repository name: " REPO_NAME
    fi
    
    print_success "Using repository: $REPO_OWNER/$REPO_NAME"
    
    # Confirm this is correct
    read -p "Is this correct? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        read -p "Enter repository owner (organization or username): " REPO_OWNER
        read -p "Enter repository name: " REPO_NAME
        print_success "Using repository: $REPO_OWNER/$REPO_NAME"
    fi
}

# Create and configure the environment
setup_environment() {
    ENV_NAME=$1
    print_status "Setting up '$ENV_NAME' environment..."
    
    # Check if environment exists
    if gh api -X GET repos/$REPO_OWNER/$REPO_NAME/environments/$ENV_NAME &> /dev/null; then
        print_status "Environment '$ENV_NAME' already exists"
    else
        print_status "Creating environment '$ENV_NAME'..."
        
        # Create the environment using GitHub API
        gh api -X PUT repos/$REPO_OWNER/$REPO_NAME/environments/$ENV_NAME --silent || {
            print_error "Failed to create environment '$ENV_NAME'"
            return 1
        }
        
        print_success "Environment '$ENV_NAME' created"
    fi
    
    # Add secrets to the environment
    print_status "Adding secrets to '$ENV_NAME' environment..."
    
    # Check if credentials file exists
    CREDS_FILE="github-azure-credentials.json"
    if [[ ! -f $CREDS_FILE ]]; then
        print_error "Credentials file '$CREDS_FILE' not found!"
        print_status "Creating sample file for you to edit..."
        
        cat > $CREDS_FILE << EOF
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "tenantId": "YOUR_TENANT_ID",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
EOF
        
        print_status "Please edit $CREDS_FILE with your Azure credentials then run this script again."
        return 1
    fi
    
    # Add Azure credentials secret to environment
    CREDS=$(cat $CREDS_FILE)
    gh secret set AZURE_CREDENTIALS --env $ENV_NAME --body "$CREDS" --repo $REPO_OWNER/$REPO_NAME || {
        print_error "Failed to set AZURE_CREDENTIALS secret for environment '$ENV_NAME'"
        return 1
    }
    
    print_success "Added AZURE_CREDENTIALS secret to '$ENV_NAME' environment"
    
    # Configure environment protection rules
    print_status "Configuring protection rules for '$ENV_NAME' environment..."
    
    # Ask if user wants to set up protection rules
    read -p "Set up protection rules for $ENV_NAME? (y/N): " setup_protection
    
    if [[ $setup_protection =~ ^[Yy]$ ]]; then
        # Get main branch name
        MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
        
        read -p "Add deployment branch restrictions? (y/N): " add_branch_restrictions
        
        if [[ $add_branch_restrictions =~ ^[Yy]$ ]]; then
            read -p "Enter allowed branch patterns (comma-separated, e.g. main,website-plan): " BRANCH_PATTERNS
            
            # If no input, use main branch and current branch
            if [[ -z $BRANCH_PATTERNS ]]; then
                CURRENT_BRANCH=$(git branch --show-current)
                BRANCH_PATTERNS="$MAIN_BRANCH,$CURRENT_BRANCH"
            fi
            
            # Convert comma-separated list to JSON array
            BRANCH_LIST=$(echo $BRANCH_PATTERNS | sed 's/,/","/g')
            BRANCH_LIST="[\"$BRANCH_LIST\"]"
            
            # Create JSON payload for environment protection rules
            PROTECTION_PAYLOAD="{\"deployment_branch_policy\":{\"protected_branches\":false,\"custom_branch_policies\":true},\"deployment_branch_policy.custom_branch_policies\":{\"branch_patterns\":$BRANCH_LIST}}"
            
            # Update environment protection rules
            gh api -X PUT repos/$REPO_OWNER/$REPO_NAME/environments/$ENV_NAME \
                -F deployment_branch_policy='{
                  "protected_branches": false,
                  "custom_branch_policies": true
                }' \
                -F deployment_branch_policy.custom_branch_policies="{
                  \"branch_patterns\": $BRANCH_LIST
                }" --silent || {
                print_warning "Failed to set branch restrictions. Using GitHub web interface is recommended."
            }
            
            print_success "Branch restrictions added for: $BRANCH_PATTERNS"
        fi
    fi
}

# Main function
main() {
    print_header
    
    echo "This script will set up GitHub environments and secrets for your"
    echo "GitHub Actions Azure deployment workflow."
    echo ""
    echo "Requirements:"
    echo "- GitHub CLI installed (or will be installed)"
    echo "- Logged in to GitHub"
    echo "- Azure credentials file (github-azure-credentials.json)"
    echo ""
    
    read -p "Continue? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        echo "Setup canceled."
        exit 0
    fi
    
    # Check GitHub CLI
    check_gh_cli
    
    # Check GitHub login
    check_gh_login
    
    # Get repository info
    get_repo_info
    
    echo ""
    echo "🌐 Setting up environments for $REPO_OWNER/$REPO_NAME"
    echo "-------------------------------------------"
    
    # Set up production environment
    setup_environment "production"
    
    # Ask if user wants to set up staging environment
    read -p "Set up staging environment as well? (y/N): " setup_staging
    if [[ $setup_staging =~ ^[Yy]$ ]]; then
        setup_environment "staging"
    fi
    
    echo ""
    print_success "🎉 GitHub environments setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to GitHub Actions tab and re-run the failed workflow"
    echo "2. Monitor the deployment progress"
    echo "3. Check the deployed resources in Azure Portal"
    echo ""
}

# Run main function
main
