#!/bin/bash

# Oracle Cloud Infrastructure Setup for AI Video Platform
# Run this after signing up for Oracle Always Free

echo "🏗️ Setting up Oracle Cloud Infrastructure for AI Video Platform"
echo "=============================================================="

# Configuration
COMPARTMENT_ID="your-compartment-id"
REGION="us-ashburn-1"  # Oracle's main region

echo "📋 Oracle Cloud Configuration:"
echo "   Compartment: $COMPARTMENT_ID"
echo "   Region: $REGION"
echo ""

# 1. Create VCN (Virtual Cloud Network)
echo "🌐 Creating Virtual Cloud Network..."
oci network vcn create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "ai-video-vcn" \
    --cidr-block "10.0.0.0/16"

# 2. Create Internet Gateway
echo "🌐 Creating Internet Gateway..."
VCN_ID=$(oci network vcn list --compartment-id $COMPARTMENT_ID --query 'data[0].id' --raw-output)
oci network internet-gateway create \
    --compartment-id $COMPARTMENT_ID \
    --vcn-id $VCN_ID \
    --display-name "ai-video-igw" \
    --is-enabled true

# 3. Create Public Subnet
echo "🏗️ Creating Public Subnet..."
IGW_ID=$(oci network internet-gateway list --compartment-id $COMPARTMENT_ID --vcn-id $VCN_ID --query 'data[0].id' --raw-output)
oci network subnet create \
    --compartment-id $COMPARTMENT_ID \
    --vcn-id $VCN_ID \
    --display-name "ai-video-public-subnet" \
    --cidr-block "10.0.1.0/24" \
    --route-table-id "default-route-table-id"

# 4. Create Security List Rules
echo "🔒 Creating Security Rules..."
SUBNET_ID=$(oci network subnet list --compartment-id $COMPARTMENT_ID --vcn-id $VCN_ID --query 'data[0].id' --raw-output)

# Allow HTTP/HTTPS traffic
oci network security-list update \
    --security-list-id "default-security-list-id" \
    --ingress-security-rules '[
        {
            "protocol": "6",
            "source": "0.0.0.0/0",
            "tcpOptions": {
                "destinationPortRange": {
                    "min": 80,
                    "max": 80
                }
            }
        },
        {
            "protocol": "6",
            "source": "0.0.0.0/0",
            "tcpOptions": {
                "destinationPortRange": {
                    "min": 443,
                    "max": 443
                }
            }
        },
        {
            "protocol": "6",
            "source": "0.0.0.0/0",
            "tcpOptions": {
                "destinationPortRange": {
                    "min": 8080,
                    "max": 8080
                }
            }
        }
    ]'

# 5. Create Always Free Compute Instances
echo "💻 Creating Always Free Compute Instances..."

# Web Server Instance
oci compute instance launch \
    --compartment-id $COMPARTMENT_ID \
    --availability-domain "AD-1" \
    --display-name "ai-video-web-server" \
    --image-id "ocid1.image.oc1..ubuntu-20-04" \
    --shape "VM.Standard.E2.1.Micro" \
    --subnet-id $SUBNET_ID \
    --assign-public-ip true \
    --ssh-authorized-keys-file ~/.ssh/id_rsa.pub

# Database Instance  
oci compute instance launch \
    --compartment-id $COMPARTMENT_ID \
    --availability-domain "AD-2" \
    --display-name "ai-video-database" \
    --image-id "ocid1.image.oc1..ubuntu-20-04" \
    --shape "VM.Standard.E2.1.Micro" \
    --subnet-id $SUBNET_ID \
    --assign-public-ip false \
    --ssh-authorized-keys-file ~/.ssh/id_rsa.pub

# 6. Create Object Storage Buckets
echo "📦 Creating Object Storage Buckets..."
oci os bucket create \
    --compartment-id $COMPARTMENT_ID \
    --name "ai-video-assets" \
    --public-access-type "ObjectRead"

oci os bucket create \
    --compartment-id $COMPARTMENT_ID \
    --name "ai-video-processed" \
    --public-access-type "ObjectRead"

oci os bucket create \
    --compartment-id $COMPARTMENT_ID \
    --name "ai-video-templates" \
    --public-access-type "ObjectRead"

# 7. Create Load Balancer (Always Free)
echo "⚖️ Creating Load Balancer..."
oci lb load-balancer create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "ai-video-lb" \
    --shape-name "10Mbps-Micro" \
    --subnet-ids '["'$SUBNET_ID'"]' \
    --is-private false

echo ""
echo "🎉 Oracle Cloud Infrastructure Setup Complete!"
echo "============================================="
echo "📋 Resources created:"
echo "   VCN: ai-video-vcn"
echo "   Compute: 2x Always Free instances"
echo "   Storage: 3x Object Storage buckets"
echo "   Load Balancer: 10Mbps Always Free"
echo ""
echo "💡 Next: Set up Google Cloud for GPU processing"
echo "🚀 Your Oracle infrastructure is ready for video platform!"
