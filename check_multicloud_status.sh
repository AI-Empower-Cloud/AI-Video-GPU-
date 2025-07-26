#!/bin/bash
# Multi-Cloud Status Checker

echo "🌐 Multi-Cloud Platform Status Check"
echo "=================================="

# Check Azure
echo "🔵 Azure:"
if az account show >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
    echo "  📊 Subscription: $(az account show --query name -o tsv)"
else
    echo "  ❌ Not authenticated"
fi

# Check GCP
echo "🟢 Google Cloud:"
if gcloud auth list --filter=status:ACTIVE --format="value(account)" >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
    echo "  📊 Project: $(gcloud config get-value project 2>/dev/null)"
else
    echo "  ❌ Not authenticated - run 'gcloud auth login'"
fi

# Check AWS
echo "🟠 AWS:"
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
    echo "  📊 Account: $(aws sts get-caller-identity --query Account --output text)"
else
    echo "  ❌ Not authenticated or account not verified"
fi

# Check Oracle Cloud
echo "🔴 Oracle Cloud:"
if oci iam user get --user-id $(oci iam user list --query 'data[0].id' --raw-output 2>/dev/null) >/dev/null 2>&1; then
    echo "  ✅ CLI authenticated"
else
    echo "  ❌ Not authenticated or account not verified"
fi
