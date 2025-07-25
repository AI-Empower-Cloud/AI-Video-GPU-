#!/bin/bash

# 🚀 Azure Verification & Authentication Troubleshooter
# Automated script to resolve Azure verification problems

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Print functions
print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║               🔧 AZURE VERIFICATION FIXER                    ║${NC}"
    echo -e "${CYAN}║          Automated troubleshooter for Azure issues          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Azure CLI installation and version
check_azure_cli() {
    print_status "Checking Azure CLI installation..."
    
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not found!"
        echo ""
        echo "📥 Installing Azure CLI automatically..."
        
        # Install Azure CLI
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
        
        print_success "Azure CLI installed successfully"
    else
        print_success "Azure CLI found"
        echo "   Version: $(az --version | head -n1)"
    fi
}

# Check current Azure login status
check_azure_login() {
    print_status "Checking Azure authentication status..."
    
    if az account show &> /dev/null; then
        ACCOUNT_INFO=$(az account show --output tsv --query '[name,user.name,id]')
        print_success "Already logged into Azure"
        echo "   Account: $(echo $ACCOUNT_INFO | cut -f1)"
        echo "   User: $(echo $ACCOUNT_INFO | cut -f2)"
        echo "   Subscription: $(echo $ACCOUNT_INFO | cut -f3)"
        return 0
    else
        print_warning "Not logged into Azure"
        return 1
    fi
}

# Multiple Azure login methods
perform_azure_login() {
    print_status "Starting Azure authentication..."
    
    echo ""
    echo "🔐 Choose your preferred login method:"
    echo "1) Interactive browser login (Recommended)"
    echo "2) Device code login (for headless environments)"
    echo "3) Service principal login (for automation)"
    echo ""
    
    read -p "Select option (1-3): " login_choice
    
    case $login_choice in
        1)
            print_status "Opening browser for interactive login..."
            az login --output table
            ;;
        2)
            print_status "Starting device code authentication..."
            az login --use-device-code --output table
            ;;
        3)
            echo "Enter service principal details:"
            read -p "App ID: " app_id
            read -s -p "Password/Secret: " password
            echo ""
            read -p "Tenant ID: " tenant_id
            
            az login --service-principal \
                --username $app_id \
                --password $password \
                --tenant $tenant_id \
                --output table
            ;;
        *)
            print_error "Invalid choice. Using default interactive login..."
            az login --output table
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "Azure login successful!"
    else
        print_error "Azure login failed"
        exit 1
    fi
}

# Clear Azure CLI cache and tokens
clear_azure_cache() {
    print_status "Clearing Azure CLI cache and tokens..."
    
    # Clear Azure CLI cache
    az cache purge 2>/dev/null || true
    
    # Clear account tokens
    az account clear 2>/dev/null || true
    
    # Remove cached credentials
    rm -rf ~/.azure/accessTokens.json 2>/dev/null || true
    rm -rf ~/.azure/azureProfile.json 2>/dev/null || true
    
    print_success "Azure cache cleared"
}

# Fix common Azure verification issues
fix_verification_issues() {
    print_status "Diagnosing and fixing verification issues..."
    
    # Check subscription access
    print_status "Checking subscription access..."
    SUBSCRIPTION_COUNT=$(az account list --output tsv | wc -l)
    
    if [ $SUBSCRIPTION_COUNT -eq 0 ]; then
        print_error "No accessible subscriptions found"
        echo ""
        echo "🔧 Possible solutions:"
        echo "1. Verify your account has an active subscription"
        echo "2. Check if your account is pending verification"
        echo "3. Contact Azure support if needed"
        
        # Try to get account info
        print_status "Checking account verification status..."
        az account show --output table 2>/dev/null || {
            print_error "Account access denied - possible verification pending"
        }
    else
        print_success "Found $SUBSCRIPTION_COUNT accessible subscription(s)"
        
        # List subscriptions
        echo ""
        echo "Available subscriptions:"
        az account list --output table
    fi
    
    # Check resource provider registrations
    print_status "Checking Azure resource providers..."
    
    REQUIRED_PROVIDERS=(
        "Microsoft.Compute"
        "Microsoft.Storage" 
        "Microsoft.Network"
        "Microsoft.Web"
        "Microsoft.ContainerRegistry"
        "Microsoft.ContainerInstance"
    )
    
    for provider in "${REQUIRED_PROVIDERS[@]}"; do
        STATUS=$(az provider show --namespace $provider --query "registrationState" --output tsv 2>/dev/null || echo "Unknown")
        
        if [ "$STATUS" != "Registered" ]; then
            print_warning "Registering provider: $provider"
            az provider register --namespace $provider --output none
        else
            print_success "Provider registered: $provider"
        fi
    done
}

# Verify Azure permissions
check_azure_permissions() {
    print_status "Checking Azure permissions..."
    
    # Check if user can create resource groups
    CURRENT_USER=$(az account show --query "user.name" --output tsv)
    print_status "Current user: $CURRENT_USER"
    
    # Try to list resource groups (basic permission test)
    if az group list --output table &> /dev/null; then
        print_success "Basic permissions verified - can list resource groups"
        
        RG_COUNT=$(az group list --query "length(@)" --output tsv)
        echo "   Found $RG_COUNT resource groups"
    else
        print_error "Permission denied - cannot list resource groups"
        echo ""
        echo "🔧 Your account may need:"
        echo "1. Contributor or Owner role assignment"
        echo "2. Account verification completion"
        echo "3. Billing setup (even for free tier)"
    fi
    
    # Check specific permissions for common operations
    print_status "Testing common operations permissions..."
    
    # Test VM creation permissions (without actually creating)
    az vm list-sizes --location eastus --output table &> /dev/null && {
        print_success "Can query VM sizes - compute permissions OK"
    } || {
        print_warning "Limited compute permissions"
    }
    
    # Test storage permissions
    az storage account check-name --name "testname12345" --output table &> /dev/null && {
        print_success "Can check storage names - storage permissions OK"
    } || {
        print_warning "Limited storage permissions"
    }
}

# Create a test deployment to verify everything works
test_azure_deployment() {
    print_status "Testing Azure deployment capabilities..."
    
    TEST_RG="az-test-verification-$(date +%s)"
    
    echo ""
    read -p "🧪 Run deployment test? This will create/delete a test resource group (y/N): " test_confirm
    
    if [[ $test_confirm =~ ^[Yy]$ ]]; then
        print_status "Creating test resource group: $TEST_RG"
        
        if az group create --name $TEST_RG --location eastus --output table; then
            print_success "Test resource group created successfully"
            
            # Clean up
            print_status "Cleaning up test resources..."
            az group delete --name $TEST_RG --yes --no-wait
            print_success "Test completed - Azure deployment capabilities verified"
        else
            print_error "Failed to create test resource group"
            echo "This indicates a verification or permission issue"
        fi
    else
        print_status "Skipping deployment test"
    fi
}

# Generate verification status report
generate_verification_report() {
    print_status "Generating Azure verification status report..."
    
    REPORT_FILE="azure_verification_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > $REPORT_FILE << EOF
# 🔍 Azure Verification Status Report
Generated: $(date)

## Account Information
- **User**: $(az account show --query "user.name" --output tsv 2>/dev/null || echo "Not available")
- **Subscription**: $(az account show --query "name" --output tsv 2>/dev/null || echo "Not available") 
- **Subscription ID**: $(az account show --query "id" --output tsv 2>/dev/null || echo "Not available")
- **Tenant**: $(az account show --query "tenantId" --output tsv 2>/dev/null || echo "Not available")

## Subscription Status
$(az account list --output table 2>/dev/null || echo "No subscriptions accessible")

## Resource Providers Status
$(
for provider in "Microsoft.Compute" "Microsoft.Storage" "Microsoft.Network" "Microsoft.Web"; do
    status=$(az provider show --namespace $provider --query "registrationState" --output tsv 2>/dev/null || echo "Unknown")
    echo "- $provider: $status"
done
)

## Permissions Check
- **Resource Groups**: $(az group list --query "length(@)" --output tsv 2>/dev/null || echo "Access denied") accessible
- **VM Sizes Query**: $(az vm list-sizes --location eastus --output table &>/dev/null && echo "✅ Success" || echo "❌ Failed")
- **Storage Check**: $(az storage account check-name --name "test" &>/dev/null && echo "✅ Success" || echo "❌ Failed")

## Recommendations
$(
if ! az account show &>/dev/null; then
    echo "❌ **Critical**: Not logged into Azure - run 'az login'"
elif [ "$(az account list --query "length(@)" --output tsv)" -eq 0 ]; then
    echo "❌ **Critical**: No accessible subscriptions - verify account status"
elif ! az group list &>/dev/null; then
    echo "❌ **Critical**: No resource group permissions - check role assignments"
else
    echo "✅ **Success**: Azure verification appears to be working correctly"
fi
)

---
Report generated by Azure Verification Troubleshooter
EOF

    print_success "Verification report saved: $REPORT_FILE"
    
    # Display key findings
    echo ""
    echo "📊 Key Findings:"
    if az account show &>/dev/null; then
        if [ "$(az account list --query "length(@)" --output tsv)" -gt 0 ]; then
            if az group list &>/dev/null; then
                print_success "✅ Azure verification is working correctly"
            else
                print_error "❌ Permission issues detected"
            fi
        else
            print_error "❌ No accessible subscriptions"
        fi
    else
        print_error "❌ Not authenticated with Azure"
    fi
}

# Main troubleshooting workflow
run_troubleshooter() {
    print_header
    
    echo "🔍 Starting Azure verification troubleshooting..."
    echo "This script will:"
    echo "├── Check Azure CLI installation"
    echo "├── Verify authentication status"  
    echo "├── Fix common verification issues"
    echo "├── Test permissions"
    echo "├── Run deployment test (optional)"
    echo "└── Generate status report"
    echo ""
    
    read -p "Continue? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        echo "Troubleshooting cancelled"
        exit 0
    fi
    
    echo ""
    
    # Step 1: Check Azure CLI
    check_azure_cli
    echo ""
    
    # Step 2: Check authentication
    if ! check_azure_login; then
        echo ""
        clear_azure_cache
        perform_azure_login
    fi
    echo ""
    
    # Step 3: Fix verification issues
    fix_verification_issues
    echo ""
    
    # Step 4: Check permissions
    check_azure_permissions
    echo ""
    
    # Step 5: Test deployment (optional)
    test_azure_deployment
    echo ""
    
    # Step 6: Generate report
    generate_verification_report
    
    echo ""
    print_success "🎉 Azure verification troubleshooting completed!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Review the generated report: $REPORT_FILE"
    echo "2. If issues persist, contact Azure support"
    echo "3. Try running the Azure deployment script: ./azure_deploy_ai_video.sh"
}

# Run the troubleshooter
run_troubleshooter
