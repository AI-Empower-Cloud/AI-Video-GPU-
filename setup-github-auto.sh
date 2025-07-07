#!/bin/bash
# GitHub Rulesets Auto-Setup Script for 2-Person Team
# This script automatically configures GitHub rulesets, secrets, and team settings

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_OWNER=""  # Will be detected automatically
REPO_NAME=""   # Will be detected automatically
GITHUB_USERNAME=""  # You'll need to set this
ROBO3_USERNAME="Robo3"  # Adjust if different

echo -e "${BLUE}🚀 GitHub Rulesets Auto-Setup for AI Video GPU${NC}"
echo -e "${BLUE}=================================================${NC}"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo -e "${YELLOW}📦 Installing GitHub CLI...${NC}"

    # Install GitHub CLI based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update
        sudo apt install gh -y
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install gh
    else
        echo -e "${RED}❌ Unsupported OS. Please install GitHub CLI manually: https://cli.github.com/${NC}"
        exit 1
    fi
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}🔐 Please authenticate with GitHub CLI...${NC}"
    gh auth login
fi

# Get repository information
REPO_INFO=$(gh repo view --json owner,name)
REPO_OWNER=$(echo $REPO_INFO | jq -r '.owner.login')
REPO_NAME=$(echo $REPO_INFO | jq -r '.name')
GITHUB_USERNAME=$(gh api user --jq '.login')

echo -e "${GREEN}✅ Repository: ${REPO_OWNER}/${REPO_NAME}${NC}"
echo -e "${GREEN}✅ Your username: ${GITHUB_USERNAME}${NC}"

# Function to create rulesets using GitHub API
create_ruleset() {
    local name=$1
    local target_branch=$2
    local required_checks=$3

    echo -e "${YELLOW}📋 Creating ruleset: ${name}${NC}"

    # Create the ruleset JSON
    local ruleset_json=$(cat <<EOF
{
  "name": "${name}",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["${target_branch}"],
      "exclude": []
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "required_status_checks": ${required_checks},
        "strict_required_status_checks_policy": true
      }
    }
  ],
  "bypass_actors": [
    {
      "actor_id": 1,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ]
}
EOF
    )

    # Create the ruleset
    gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "/repos/${REPO_OWNER}/${REPO_NAME}/rulesets" \
        --input - <<< "$ruleset_json"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully created ruleset: ${name}${NC}"
    else
        echo -e "${RED}❌ Failed to create ruleset: ${name}${NC}"
    fi
}

# Function to set repository secrets
set_secret() {
    local secret_name=$1
    local secret_value=$2

    echo -e "${YELLOW}🔐 Setting secret: ${secret_name}${NC}"

    if [ -n "$secret_value" ]; then
        echo "$secret_value" | gh secret set "$secret_name"
        echo -e "${GREEN}✅ Successfully set secret: ${secret_name}${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping empty secret: ${secret_name}${NC}"
    fi
}

# Function to add collaborator
add_collaborator() {
    local username=$1
    local permission=$2

    echo -e "${YELLOW}👥 Adding collaborator: ${username} with ${permission} permission${NC}"

    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "/repos/${REPO_OWNER}/${REPO_NAME}/collaborators/${username}" \
        -f permission="$permission"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully added collaborator: ${username}${NC}"
    else
        echo -e "${YELLOW}⚠️  Collaborator ${username} may already exist or be pending${NC}"
    fi
}

echo -e "\n${BLUE}🔧 Step 1: Creating Branch Protection Rulesets${NC}"

# Required status checks for main branch
MAIN_CHECKS='[
    {"context": "test (3.8)"},
    {"context": "test (3.9)"},
    {"context": "test (3.10)"},
    {"context": "test (3.11)"},
    {"context": "quality"},
    {"context": "wasabi-tests"}
]'

# Required status checks for develop branch
DEVELOP_CHECKS='[
    {"context": "test (3.8)"},
    {"context": "test (3.9)"},
    {"context": "test (3.10)"},
    {"context": "test (3.11)"},
    {"context": "quality"}
]'

# Create rulesets
create_ruleset "main-branch-protection" "main" "$MAIN_CHECKS"
create_ruleset "develop-branch-protection" "develop" "$DEVELOP_CHECKS"

echo -e "\n${BLUE}🔐 Step 2: Setting up GitHub Secrets${NC}"

# Check if .env file exists and read Wasabi credentials
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
    echo -e "${YELLOW}⚠️  .env file not found. Please set Wasabi secrets manually in GitHub Settings.${NC}"
fi

echo -e "\n${BLUE}👥 Step 3: Setting up Team Access${NC}"

# Add Robo3 as collaborator with admin access
add_collaborator "$ROBO3_USERNAME" "admin"

echo -e "\n${BLUE}📝 Step 4: Updating CODEOWNERS file${NC}"

# Update CODEOWNERS file with actual usernames
if [ -f ".github/CODEOWNERS" ]; then
    echo -e "${YELLOW}📝 Updating CODEOWNERS with actual usernames...${NC}"

    # Create backup
    cp .github/CODEOWNERS .github/CODEOWNERS.backup

    # Replace placeholders with actual usernames
    sed -i "s/@YOUR_USERNAME/@${GITHUB_USERNAME}/g" .github/CODEOWNERS
    sed -i "s/@Robo3/@${ROBO3_USERNAME}/g" .github/CODEOWNERS

    echo -e "${GREEN}✅ Updated CODEOWNERS file${NC}"

    # Commit the changes
    git add .github/CODEOWNERS
    git commit -m "Update CODEOWNERS with actual GitHub usernames" || echo -e "${YELLOW}⚠️  No changes to commit in CODEOWNERS${NC}"
fi

echo -e "\n${BLUE}🎯 Step 5: Final Configuration${NC}"

# Enable repository features
echo -e "${YELLOW}🔧 Enabling repository features...${NC}"

gh api \
    --method PATCH \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/${REPO_OWNER}/${REPO_NAME}" \
    -f has_issues=true \
    -f has_projects=true \
    -f has_wiki=false \
    -f allow_squash_merge=true \
    -f allow_merge_commit=false \
    -f allow_rebase_merge=true \
    -f delete_branch_on_merge=true

echo -e "\n${GREEN}🎉 GitHub Repository Setup Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"

echo -e "\n${BLUE}📋 Summary of what was configured:${NC}"
echo -e "✅ Branch protection rulesets for main and develop"
echo -e "✅ Required status checks for all Python versions"
echo -e "✅ Pull request requirements (1 reviewer)"
echo -e "✅ GitHub secrets for Wasabi integration"
echo -e "✅ Team access for ${ROBO3_USERNAME}"
echo -e "✅ Updated CODEOWNERS file"
echo -e "✅ Repository settings optimized"

echo -e "\n${BLUE}🚀 Next Steps:${NC}"
echo -e "1. Invite ${ROBO3_USERNAME} to the repository (they'll get an email invitation)"
echo -e "2. Create a test branch and PR to verify the rules work"
echo -e "3. Start using the feature branch workflow"

echo -e "\n${BLUE}🔗 Useful Links:${NC}"
echo -e "Repository: https://github.com/${REPO_OWNER}/${REPO_NAME}"
echo -e "Settings: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings"
echo -e "Rulesets: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/rules"
echo -e "Actions: https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"

echo -e "\n${GREEN}✨ Your AI Video GPU repository is now production-ready!${NC}"
