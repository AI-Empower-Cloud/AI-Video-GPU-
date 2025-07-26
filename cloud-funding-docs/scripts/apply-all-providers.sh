#!/bin/bash

# Master script to coordinate all cloud provider applications
echo "🎯 Master Cloud Provider Application System"
echo "==========================================="

# Phase 1: Immediate Free Tiers
echo "🚀 Phase 1: Free Tier Signups (Today)"
echo "======================================"

free_tier_providers=(
    "Oracle Cloud Always Free|https://oracle.com/cloud/free|Always Free"
    "Google Cloud Free Tier|https://cloud.google.com/free|\$300 credits"
    "IBM Cloud Lite|https://ibm.com/cloud/free|\$200 credits"
    "DigitalOcean Free|https://digitalocean.com|\$200 credits"
)

for provider in "${free_tier_providers[@]}"; do
    IFS='|' read -r name url credits <<< "$provider"
    echo "✅ $name: $credits"
    echo "   Apply at: $url"
    echo ""
done

# Phase 2: Major Startup Programs
echo "💰 Phase 2: Major Startup Programs (This Week)"
echo "==============================================="

startup_programs=(
    "Microsoft Azure for Startups|https://startups.microsoft.com|\$25,000+"
    "Google Cloud for Startups|https://cloud.google.com/startup|\$20,000+"
    "AWS Activate|https://aws.amazon.com/activate|\$10,000+"
    "IBM Cloud for Startups|https://developer.ibm.com/startups|\$12,000+"
)

for provider in "${startup_programs[@]}"; do
    IFS='|' read -r name url credits <<< "$provider"
    echo "📋 $name: $credits"
    echo "   Apply at: $url"
    echo ""
done

# Phase 3: Specialized AI/ML Providers
echo "🤖 Phase 3: AI/ML Specialized (Next Week)"
echo "=========================================="

ai_providers=(
    "NVIDIA Cloud|https://developer.nvidia.com|\$5,000+"
    "Lambda Labs|https://lambdalabs.com|\$3,000+"
    "Paperspace|https://paperspace.com|\$2,500+"
    "Weights & Biases|https://wandb.ai|\$5,000+"
)

for provider in "${ai_providers[@]}"; do
    IFS='|' read -r name url credits <<< "$provider"
    echo "🧠 $name: $credits"
    echo "   Apply at: $url"
    echo ""
done

# Phase 4: Enterprise Programs
echo "🏢 Phase 4: Enterprise Programs (Month 2+)"
echo "=========================================="

enterprise_programs=(
    "Microsoft for Startups Founders Hub|https://startups.microsoft.com/founder-hub|\$120,000+"
    "Techstars Cloud Credits|https://techstars.com|\$100,000+"
    "Google for Startups|https://startup.google.com|\$100,000+"
)

for provider in "${enterprise_programs[@]}"; do
    IFS='|' read -r name url credits <<< "$provider"
    echo "🏆 $name: $credits"
    echo "   Apply at: $url"
    echo ""
done

echo "📊 Total Potential Credits: $357,000+"
echo ""
echo "🎯 Next Steps:"
echo "1. Start with Phase 1 free tiers (immediate)"
echo "2. Apply to Phase 2 programs (this week)"  
echo "3. Follow up on applications weekly"
echo "4. Update tracking spreadsheet regularly"
echo ""
echo "💡 Success tip: Apply systematically and track everything!"
