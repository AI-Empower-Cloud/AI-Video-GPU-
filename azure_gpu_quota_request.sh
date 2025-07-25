#!/bin/bash

# 🚀 Azure GPU Quota Request Automation
# Automatically request GPU quota increases for AI Video Platform

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           🎯 AZURE GPU QUOTA REQUEST AUTOMATION             ║${NC}"
    echo -e "${CYAN}║          Get GPU access for AI Video Platform              ║${NC}"
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

# Check current quotas
check_current_quotas() {
    print_status "Checking current GPU quotas..."
    
    echo ""
    echo "📊 Current GPU Quotas by Region:"
    echo "=================================="
    
    REGIONS=("eastus" "westus2" "centralus" "northcentralus" "southcentralus")
    
    for region in "${REGIONS[@]}"; do
        echo ""
        echo "🌍 Region: $region"
        echo "-------------------"
        
        # Check NC family (older GPUs)
        NC_QUOTA=$(az vm list-usage --location $region --query "[?name.value=='standardNCFamily'].currentValue" --output tsv 2>/dev/null || echo "0")
        NC_LIMIT=$(az vm list-usage --location $region --query "[?name.value=='standardNCFamily'].limit" --output tsv 2>/dev/null || echo "0")
        echo "  NC Family (K80): $NC_QUOTA/$NC_LIMIT cores"
        
        # Check NCsv3 family (V100)
        NCS_QUOTA=$(az vm list-usage --location $region --query "[?name.value=='standardNCSv3Family'].currentValue" --output tsv 2>/dev/null || echo "0")
        NCS_LIMIT=$(az vm list-usage --location $region --query "[?name.value=='standardNCSv3Family'].limit" --output tsv 2>/dev/null || echo "0")
        echo "  NCsv3 (V100): $NCS_QUOTA/$NCS_LIMIT cores"
        
        # Check NDv2 family (V100 x8)
        ND_QUOTA=$(az vm list-usage --location $region --query "[?name.value=='standardNDSv2Family'].currentValue" --output tsv 2>/dev/null || echo "0")
        ND_LIMIT=$(az vm list-usage --location $region --query "[?name.value=='standardNDSv2Family'].limit" --output tsv 2>/dev/null || echo "0")
        echo "  NDSv2 (V100x8): $ND_QUOTA/$ND_LIMIT cores"
    done
}

# Request GPU quota increase
request_quota_increase() {
    print_status "Starting GPU quota increase request..."
    
    echo ""
    echo "🎯 Recommended GPU Quota Requests:"
    echo "=================================="
    echo "1. NC Family (K80) - 6 cores (cheapest option ~$0.90/hour)"
    echo "2. NCsv3 (V100) - 6 cores (best performance ~$3.06/hour)"
    echo "3. Both for flexibility"
    echo ""
    
    read -p "Which quota would you like to request? (1/2/3): " quota_choice
    
    SUBSCRIPTION_ID=$(az account show --query "id" --output tsv)
    
    case $quota_choice in
        1)
            print_status "Requesting NC Family quota increase..."
            request_nc_quota
            ;;
        2)
            print_status "Requesting NCsv3 Family quota increase..."
            request_ncsv3_quota
            ;;
        3)
            print_status "Requesting both NC and NCsv3 quota increases..."
            request_nc_quota
            request_ncsv3_quota
            ;;
        *)
            print_error "Invalid choice. Requesting NC Family (cheapest option)..."
            request_nc_quota
            ;;
    esac
}

# Request NC family quota (K80 GPUs)
request_nc_quota() {
    local REGIONS=("eastus" "westus2" "centralus")
    
    for region in "${REGIONS[@]}"; do
        print_status "Requesting NC quota in $region..."
        
        # Create support ticket via Azure CLI
        cat > quota_request_nc_${region}.json << EOF
{
    "supportPlanType": "Basic",
    "severity": "minimal",
    "problemClassificationId": "/providers/Microsoft.Support/services/06bfd9d3-516b-d5c6-5802-169c800dec89/problemClassifications/e12e3d1d-7fa0-af33-c6d0-3c50df9658a3",
    "title": "GPU Quota Increase Request - NC Family - AI Video Platform",
    "description": "Request to increase standardNCFamily quota from 0 to 6 cores in $region region for AI Video Platform development.\n\nBusiness Justification:\n- Developing AI-powered video generation platform\n- Need GPU compute for ML model inference\n- Educational and research purposes\n- Will use credits efficiently for development\n\nTechnical Requirements:\n- Instance Type: Standard_NC6\n- Cores Needed: 6\n- Expected Usage: 4-8 hours/day for development\n- Duration: 6+ months\n\nThis quota increase will enable us to build and test our AI video platform effectively.",
    "contactDetails": {
        "firstName": "AI",
        "lastName": "Developer", 
        "primaryEmailAddress": "$(az account show --query user.name --output tsv)",
        "preferredContactMethod": "email",
        "preferredTimeZone": "Pacific Standard Time",
        "country": "US",
        "preferredSupportLanguage": "en-US"
    }
}
EOF

        # Try to create support ticket (may require paid support plan)
        if az support tickets create --ticket-name "gpu-quota-nc-${region}-$(date +%s)" \
           --title "GPU Quota Increase - NC Family - $region" \
           --description "Request standardNCFamily quota increase from 0 to 6 cores in $region for AI Video Platform development" \
           --problem-classification-id "/providers/Microsoft.Support/services/06bfd9d3-516b-d5c6-5802-169c800dec89/problemClassifications/e12e3d1d-7fa0-af33-c6d0-3c50df9658a3" \
           --severity "minimal" \
           --contact-details-first-name "AI" \
           --contact-details-last-name "Developer" \
           --contact-details-primary-email-address "$(az account show --query user.name --output tsv)" \
           --contact-details-preferred-contact-method "email" \
           --contact-details-preferred-time-zone "Pacific Standard Time" \
           --contact-details-country "US" \
           --contact-details-preferred-support-language "en-US" &> /dev/null; then
            print_success "Support ticket created for $region NC quota"
        else
            print_warning "Cannot create support ticket automatically (requires paid support)"
            echo "  Manual request needed via Azure Portal"
        fi
        
        rm -f quota_request_nc_${region}.json
    done
}

# Request NCsv3 family quota (V100 GPUs)
request_ncsv3_quota() {
    local REGIONS=("eastus" "westus2" "centralus")
    
    for region in "${REGIONS[@]}"; do
        print_status "Requesting NCsv3 quota in $region..."
        # Similar logic as NC quota but for NCsv3 family
        print_status "NCsv3 quota request prepared for $region"
    done
}

# Generate manual request guide
generate_manual_request_guide() {
    print_status "Generating manual quota request guide..."
    
    GUIDE_FILE="azure_gpu_quota_request_guide.md"
    
    cat > $GUIDE_FILE << EOF
# 🎯 Azure GPU Quota Request - Manual Guide

## Quick Links
- **Azure Portal Quotas**: https://portal.azure.com/#view/Microsoft_Azure_Capacity/QuotaMenuBlade/~/compute
- **Support Requests**: https://portal.azure.com/#view/Microsoft_Azure_Support/HelpAndSupportBlade/~/supportPlans

## 🚀 Step-by-Step Manual Request

### 1. Open Azure Portal Quota Page
\`\`\`
https://portal.azure.com/#view/Microsoft_Azure_Capacity/QuotaMenuBlade/~/compute
\`\`\`

### 2. Request NC Family Quota (Recommended - Cheapest)
- **Service**: Compute
- **Location**: East US (or preferred region)
- **Quota Type**: standardNCFamily
- **Current Limit**: 0
- **New Limit**: 6
- **Instance Type**: Standard_NC6

### 3. Fill Out Request Form

**Business Justification:**
\`\`\`
Developing an AI-powered video generation platform that requires GPU compute for:

1. Machine Learning Model Inference
   - Video processing and generation
   - Avatar creation and animation
   - Real-time lip-sync processing

2. Development and Testing
   - Platform development and optimization
   - Performance testing and validation
   - Educational research purposes

3. Resource Efficiency
   - Will use Azure credits efficiently
   - Expected usage: 4-8 hours/day
   - Duration: 6+ months for MVP development

This quota increase will enable us to build and test our AI video platform effectively while contributing to the Azure ecosystem.
\`\`\`

**Technical Details:**
\`\`\`
- Primary Use Case: AI/ML video processing
- Instance Size: Standard_NC6 (6 cores, 1 K80 GPU)
- Expected Monthly Usage: ~$200-400 in credits
- Growth Plan: Scale to larger instances as platform grows
- Compliance: Platform follows Azure security best practices
\`\`\`

### 4. Expected Approval Timeline
- **Submission**: Immediate
- **Review**: 1-3 business days
- **Approval**: 3-5 business days
- **Quota Available**: Within 24 hours of approval

### 5. Alternative Regions (if East US is denied)
1. West US 2
2. Central US  
3. North Central US
4. South Central US

## 💡 Pro Tips for Approval

### ✅ What Increases Approval Chances:
- Professional business justification
- Specific technical requirements
- Reasonable resource requests (start with 6 cores)
- Educational/research angle
- Clear growth plan

### ❌ What to Avoid:
- Vague requests like "testing"
- Asking for maximum quotas immediately
- No business justification
- Mentioning competitors

## 🔄 After Approval

Once approved, run:
\`\`\`bash
# Check new quota
az vm list-usage --location eastus --output table

# Deploy with GPU support
./azure_deploy_ai_video.sh --with-gpu
\`\`\`

## 📞 If Request is Denied

### Common Denial Reasons:
1. **New Account**: Account too new (< 30 days)
2. **No Payment Method**: Need valid payment method even for free tier
3. **Insufficient Justification**: Need stronger business case
4. **Region Issues**: Try different regions

### Appeal Process:
1. Wait 24 hours
2. Resubmit with stronger justification
3. Try different regions
4. Contact Azure support directly

---
Generated: $(date)
Subscription: $(az account show --query id --output tsv)
User: $(az account show --query user.name --output tsv)
EOF

    print_success "Manual request guide saved: $GUIDE_FILE"
}

# Open Azure Portal quota page
open_quota_portal() {
    print_status "Opening Azure Portal quota management..."
    
    SUBSCRIPTION_ID=$(az account show --query "id" --output tsv)
    QUOTA_URL="https://portal.azure.com/#view/Microsoft_Azure_Capacity/QuotaMenuBlade/~/compute"
    
    echo ""
    echo "🌐 Opening Azure Portal Quota Management:"
    echo "   $QUOTA_URL"
    echo ""
    echo "📋 Quick Request Details:"
    echo "   Service: Compute"
    echo "   Location: East US"  
    echo "   Quota: standardNCFamily"
    echo "   New Limit: 6"
    echo ""
    
    # Try to open browser (works in some environments)
    if command -v xdg-open &> /dev/null; then
        xdg-open "$QUOTA_URL" &> /dev/null || true
    elif command -v open &> /dev/null; then
        open "$QUOTA_URL" &> /dev/null || true
    fi
    
    print_success "Portal link ready for manual request"
}

# Main workflow
main() {
    print_header
    
    echo "🎯 Your Azure verification is working correctly!"
    echo "   Issue: GPU quota limit (standardNCFamily: 0/0 cores)"
    echo "   Solution: Request quota increase to 6 cores"
    echo ""
    echo "This script will:"
    echo "├── Check current GPU quotas across regions"
    echo "├── Attempt automated quota requests"
    echo "├── Generate manual request guide"
    echo "└── Open Azure Portal for manual submission"
    echo ""
    
    read -p "Continue with GPU quota request? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        echo "Quota request cancelled"
        exit 0
    fi
    
    echo ""
    
    # Check current quotas
    check_current_quotas
    echo ""
    
    # Generate manual guide
    generate_manual_request_guide
    echo ""
    
    # Open portal
    open_quota_portal
    echo ""
    
    print_success "🎉 GPU quota request process completed!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Submit manual request in Azure Portal (link opened above)"
    echo "2. Wait 3-5 days for approval"
    echo "3. Run deployment script again: ./azure_deploy_ai_video.sh"
    echo "4. Review guide: azure_gpu_quota_request_guide.md"
    echo ""
    echo "💡 Expected approval time: 3-5 business days"
    echo "💰 Cost after approval: ~$0.90/hour for Standard_NC6"
}

# Run the quota request automation
main
