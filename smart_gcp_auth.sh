#!/bin/bash

# 🚀 AI Video GPU - Smart GCP Setup
# This script will detect available authentication and proceed automatically

echo "🟢 AI Video GPU - Smart GCP Authentication Setup"
echo "================================================"

# Function to check if service account key exists
check_service_account_key() {
    if [ -f "gcp-service-account.json" ]; then
        echo "✅ Found service account key: gcp-service-account.json"
        export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcp-service-account.json"
        return 0
    fi
    return 1
}

# Function to check if gcloud is authenticated
check_gcloud_auth() {
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null 2>&1; then
        ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
        echo "✅ Found active gcloud authentication: $ACTIVE_ACCOUNT"
        return 0
    fi
    return 1
}

# Try authentication methods
echo "🔍 Checking authentication methods..."

if check_service_account_key; then
    echo "📝 Using service account key authentication"
    AUTH_METHOD="service_account"
elif check_gcloud_auth; then
    echo "📝 Using gcloud CLI authentication"
    AUTH_METHOD="gcloud_cli"
else
    echo "❌ No authentication found!"
    echo ""
    echo "Please provide authentication using one of these methods:"
    echo ""
    echo "🔑 Method 1 - Service Account Key:"
    echo "   1. Download JSON key from Google Cloud Console"
    echo "   2. Save as 'gcp-service-account.json' in this directory"
    echo "   3. Run this script again"
    echo ""
    echo "🌐 Method 2 - gcloud CLI:"
    echo "   1. Run: gcloud auth login"
    echo "   2. Follow browser authentication"
    echo "   3. Run this script again"
    echo ""
    echo "📤 Method 3 - Paste JSON Content:"
    echo "   1. Copy your service account JSON content"
    echo "   2. Tell me and I'll create the file"
    echo ""
    exit 1
fi

# Get project ID
if [ -z "$GCP_PROJECT_ID" ]; then
    if [ "$AUTH_METHOD" = "service_account" ]; then
        GCP_PROJECT_ID=$(cat gcp-service-account.json | grep -o '"project_id": "[^"]*' | cut -d'"' -f4)
    else
        GCP_PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    fi
    
    if [ -z "$GCP_PROJECT_ID" ]; then
        echo "⚠️  Project ID not found. Please enter your GCP Project ID:"
        read -p "GCP Project ID: " GCP_PROJECT_ID
    fi
fi

echo "📋 Project ID: $GCP_PROJECT_ID"
export GCP_PROJECT_ID

# Verify the service account exists
echo "🔍 Verifying service account: ai-video-gpu-service"

if [ "$AUTH_METHOD" = "service_account" ]; then
    # With service account, we assume it exists since we have the key
    echo "✅ Service account key loaded"
else
    # With gcloud CLI, check if service account exists
    if gcloud iam service-accounts describe "ai-video-gpu-service@${GCP_PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1; then
        echo "✅ Service account exists: ai-video-gpu-service@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
    else
        echo "❌ Service account not found. Creating it..."
        gcloud iam service-accounts create ai-video-gpu-service \
            --description="AI Video GPU Service Account" \
            --display-name="AI Video GPU Service"
        
        # Grant necessary roles
        echo "🔑 Granting necessary permissions..."
        ROLES=(
            "roles/editor"
            "roles/storage.admin"
            "roles/container.admin"
            "roles/aiplatform.admin"
            "roles/bigquery.admin"
        )
        
        for role in "${ROLES[@]}"; do
            gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
                --member="serviceAccount:ai-video-gpu-service@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
                --role="$role" \
                --quiet
        done
        
        echo "✅ Service account created and configured"
    fi
fi

echo ""
echo "🎉 Authentication setup complete!"
echo "📋 Configuration:"
echo "   • Project ID: $GCP_PROJECT_ID"
echo "   • Service Account: ai-video-gpu-service@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
echo "   • Authentication Method: $AUTH_METHOD"
echo ""
echo "🚀 Ready to run GCP setup: ./setup_gcp_complete.sh"

# Save configuration
cat > .env.gcp << EOF
GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID
GCP_SERVICE_ACCOUNT=ai-video-gpu-service@${GCP_PROJECT_ID}.iam.gserviceaccount.com
GCP_AUTH_METHOD=$AUTH_METHOD
EOF

echo "💾 Configuration saved to .env.gcp"
