#!/bin/bash
# GitHub Setup Script for 2-Person Team (Simplified)
# This script sets up what we can via CLI and provides manual steps for the rest

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 GitHub Auto-Setup for AI Video GPU (2-Person Team)${NC}"
echo -e "${BLUE}====================================================${NC}"

# Get repository information
REPO_INFO=$(gh repo view --json owner,name)
REPO_OWNER=$(echo $REPO_INFO | jq -r '.owner.login')
REPO_NAME=$(echo $REPO_INFO | jq -r '.name')
GITHUB_USERNAME=$(gh api user --jq '.login')

echo -e "${GREEN}✅ Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo -e "${GREEN}✅ Your username: ${GITHUB_USERNAME}${NC}"

# Function to set repository secrets
set_secret() {
    local secret_name=$1
    local secret_value=$2

    if [ -n "$secret_value" ]; then
        echo -e "${YELLOW}🔐 Setting secret: ${secret_name}${NC}"
        echo "$secret_value" | gh secret set "$secret_name"
        echo -e "${GREEN}✅ Successfully set secret: ${secret_name}${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping empty secret: ${secret_name}${NC}"
    fi
}

echo -e "\n${BLUE}🔐 Step 1: Setting up GitHub Secrets${NC}"

# Read Wasabi credentials from .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Found .env file, reading Wasabi credentials...${NC}"
    source .env

    # Set secrets from environment variables
    set_secret "WASABI_ACCESS_KEY" "$WASABI_ACCESS_KEY"
    set_secret "WASABI_SECRET_KEY" "$WASABI_SECRET_KEY"
    set_secret "WASABI_ENDPOINT_URL" "$WASABI_ENDPOINT_URL"
    set_secret "WASABI_REGION" "$WASABI_REGION"
    set_secret "WASABI_MODELS_BUCKET" "$WASABI_MODELS_BUCKET"
    set_secret "WASABI_OUTPUTS_BUCKET" "$WASABI_OUTPUTS_BUCKET"
    set_secret "WASABI_UPLOADS_BUCKET" "$WASABI_UPLOADS_BUCKET"
    set_secret "WASABI_BACKUPS_BUCKET" "$WASABI_BACKUPS_BUCKET"
    set_secret "WASABI_TEMP_BUCKET" "$WASABI_TEMP_BUCKET"
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
fi

echo -e "\n${BLUE}📝 Step 2: Updating CODEOWNERS file${NC}"

# Update CODEOWNERS file with actual usernames
if [ -f ".github/CODEOWNERS" ]; then
    echo -e "${YELLOW}📝 Updating CODEOWNERS with actual usernames...${NC}"

    # Create backup
    cp .github/CODEOWNERS .github/CODEOWNERS.backup

    # Replace placeholders with actual usernames
    sed -i "s/@YOUR_USERNAME/@${GITHUB_USERNAME}/g" .github/CODEOWNERS
    sed -i "s/@Robo3/@Robo3/g" .github/CODEOWNERS  # Keep as @Robo3 for now

    echo -e "${GREEN}✅ Updated CODEOWNERS file${NC}"

    # Show the updated content
    echo -e "${BLUE}📋 Updated CODEOWNERS content:${NC}"
    cat .github/CODEOWNERS
fi

echo -e "\n${BLUE}🔧 Step 3: Repository Settings${NC}"

# Update repository settings
echo -e "${YELLOW}🔧 Updating repository settings...${NC}"

gh api \
    --method PATCH \
    -H "Accept: application/vnd.github+json" \
    "/repos/${REPO_OWNER}/${REPO_NAME}" \
    -f allow_squash_merge=true \
    -f allow_merge_commit=false \
    -f allow_rebase_merge=true \
    -f delete_branch_on_merge=true \
    -f has_issues=true \
    -f has_projects=true \
    -f has_wiki=false

echo -e "${GREEN}✅ Repository settings updated${NC}"

echo -e "\n${GREEN}🎉 Automated Setup Complete!${NC}"
echo -e "${GREEN}==============================${NC}"

echo -e "\n${BLUE}📋 What was configured automatically:${NC}"
echo -e "✅ GitHub secrets for Wasabi integration"
echo -e "✅ Updated CODEOWNERS file with your username"
echo -e "✅ Repository settings optimized"

echo -e "\n${RED}⚠️  MANUAL STEPS REQUIRED:${NC}"
echo -e "${YELLOW}You need to manually create rulesets in GitHub web interface:${NC}"

echo -e "\n${BLUE}🎯 Manual Step 1: Create Branch Protection Rulesets${NC}"
echo -e "1. Go to: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/rules"
echo -e "2. Click 'New ruleset' → 'Branch ruleset'"
echo -e "3. Create ruleset with these settings:"
echo -e ""
echo -e "${YELLOW}Main Branch Ruleset:${NC}"
echo -e "   Name: main-branch-protection"
echo -e "   Target: main"
echo -e "   Rules to enable:"
echo -e "   ✅ Restrict deletions"
echo -e "   ✅ Restrict force pushes"
echo -e "   ✅ Require pull request (1 reviewer)"
echo -e "   ✅ Require status checks:"
echo -e "      - test (3.8)"
echo -e "      - test (3.9)"
echo -e "      - test (3.10)"
echo -e "      - test (3.11)"
echo -e "      - quality"
echo -e "      - wasabi-tests"
echo -e ""
echo -e "${YELLOW}Develop Branch Ruleset:${NC}"
echo -e "   Name: develop-branch-protection"
echo -e "   Target: develop"
echo -e "   Rules: Same as main but without wasabi-tests"

echo -e "\n${BLUE}🎯 Manual Step 2: Add Robo3 as Collaborator${NC}"
echo -e "1. Go to: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/access"
echo -e "2. Click 'Add people'"
echo -e "3. Search for 'Robo3' and add with 'Admin' permission"

echo -e "\n${BLUE}🎯 Manual Step 3: Test the Setup${NC}"
echo -e "1. Create a test branch: git checkout -b test/setup-verification"
echo -e "2. Make a small change and push"
echo -e "3. Create a PR to develop branch"
echo -e "4. Verify that status checks are required"

echo -e "\n${GREEN}🔗 Quick Links:${NC}"
echo -e "Repository: https://github.com/${REPO_OWNER}/${REPO_NAME}"
echo -e "Rulesets: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/rules"
echo -e "Collaborators: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/access"
echo -e "Actions: https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"
echo -e "Secrets: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/secrets/actions"

echo -e "\n${GREEN}✨ Ready to continue with manual steps!${NC}"
