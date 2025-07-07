#!/usr/bin/env python3
"""
Test script to verify GitHub setup is working correctly.
Run this after completing the manual GitHub setup steps.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_git_status():
    """Check if we're in a git repository with proper remotes."""
    print("🔍 Checking git status...")

    # Check if we're in a git repo
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        print("❌ Not in a git repository")
        return False

    # Check remote origin
    success, stdout, stderr = run_command("git remote -v")
    if not success or "AI-Video-GPU-" not in stdout:
        print("❌ Git remote not configured properly")
        return False

    print("✅ Git repository configured correctly")
    return True


def check_required_files():
    """Check if all required files exist."""
    print("🔍 Checking required files...")

    required_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/code-quality.yml",
        ".github/workflows/wasabi-tests.yml",
        ".github/CODEOWNERS",
        "MANUAL_GITHUB_SETUP.md",
        "requirements.txt",
        "requirements-dev.txt",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False

    print("✅ All required files present")
    return True


def create_test_branch():
    """Create a test branch to verify branch protection."""
    print("🔍 Creating test branch...")

    # Clean up any existing test branch
    run_command("git branch -D test/github-setup-verification", capture_output=True)
    run_command("git push origin --delete test/github-setup-verification", capture_output=True)

    # Create new test branch
    success, stdout, stderr = run_command("git checkout -b test/github-setup-verification")
    if not success:
        print(f"❌ Failed to create test branch: {stderr}")
        return False

    # Create a simple test file
    test_content = f"""# GitHub Setup Test
This file was created to test GitHub branch protection rules.
Created at: {subprocess.check_output(['date'], text=True).strip()}
"""

    with open("GITHUB_SETUP_TEST.md", "w") as f:
        f.write(test_content)

    # Add and commit the test file
    success, stdout, stderr = run_command("git add GITHUB_SETUP_TEST.md")
    if not success:
        print(f"❌ Failed to add test file: {stderr}")
        return False

    success, stdout, stderr = run_command('git commit -m "test: Verify GitHub setup and branch protection rules"')
    if not success:
        print(f"❌ Failed to commit test file: {stderr}")
        return False

    print("✅ Test branch created with test commit")
    return True


def push_test_branch():
    """Push the test branch to origin."""
    print("🔍 Pushing test branch to origin...")

    success, stdout, stderr = run_command("git push origin test/github-setup-verification")
    if not success:
        print(f"❌ Failed to push test branch: {stderr}")
        return False

    print("✅ Test branch pushed successfully")
    return True


def cleanup_test():
    """Clean up the test branch and file."""
    print("🔍 Cleaning up test branch...")

    # Switch back to main/develop
    run_command("git checkout main", capture_output=True)
    if not Path(".git/refs/heads/main").exists():
        run_command("git checkout develop", capture_output=True)

    # Delete test branch locally
    run_command("git branch -D test/github-setup-verification", capture_output=True)

    # Delete test file if it exists
    if Path("GITHUB_SETUP_TEST.md").exists():
        Path("GITHUB_SETUP_TEST.md").unlink()

    print("✅ Test cleanup completed")


def main():
    """Main test function."""
    print("🚀 Testing GitHub Setup...")
    print("=" * 50)

    # Check basic git setup
    if not check_git_status():
        print("❌ Git setup verification failed")
        return False

    # Check required files
    if not check_required_files():
        print("❌ Required files check failed")
        return False

    # Create test branch
    if not create_test_branch():
        print("❌ Test branch creation failed")
        return False

    # Push test branch
    if not push_test_branch():
        print("❌ Test branch push failed")
        cleanup_test()
        return False

    print("=" * 50)
    print("✅ GitHub Setup Test Completed Successfully!")
    print()
    print("🎯 Next Steps:")
    print("1. Go to your GitHub repository:")
    print("   https://github.com/AI-Empower-Cloud/AI-Video-GPU-")
    print("2. You should see a 'Compare & pull request' button")
    print("3. Create a PR from 'test/github-setup-verification' to 'develop'")
    print("4. Verify that:")
    print("   - PR shows 'Review required' status")
    print("   - GitHub Actions start running")
    print("   - Merge is blocked until review + tests pass")
    print("5. After testing, delete the test branch and PR")
    print()
    print("🔗 Manual Setup Guide: MANUAL_GITHUB_SETUP.md")

    cleanup_test()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
