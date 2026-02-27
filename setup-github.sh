#!/bin/bash
# =============================================================================
# Poetry Analyzer App - GitHub Push Script
# This script initializes git and pushes to GitHub
# =============================================================================

set -e

echo "=========================================="
echo "  Poetry Analyzer App - GitHub Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the poetry_analyzer_app directory${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Current directory: $(pwd)${NC}"
echo ""

# Step 1: Initialize git
echo -e "${BLUE}Step 1/6: Initializing Git repository...${NC}"
if [ -d ".git" ]; then
    echo -e "${GREEN}✅ Git already initialized${NC}"
else
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi
echo ""

# Step 2: Check .gitignore
echo -e "${BLUE}Step 2/6: Checking .gitignore...${NC}"
if [ -f ".gitignore" ]; then
    echo -e "${GREEN}✅ .gitignore exists${NC}"
else
    echo -e "${RED}❌ .gitignore not found! Creating...${NC}"
    cat > .gitignore << 'EOF'
# Python
.env/
venv/
__pycache__/
*.pyc
*.pyo
*.db
*.sqlite

# IDE
.idea/
.vscode/
.DS_Store

# Secrets
.env
*.key
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}"
fi
echo ""

# Step 3: Add files
echo -e "${BLUE}Step 3/6: Adding files to git...${NC}"
git add .
echo -e "${GREEN}✅ Files added${NC}"
echo ""

# Step 4: Show what will be committed
echo -e "${BLUE}Step 4/6: Files to be committed:${NC}"
git status --short
echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Aborted${NC}"
    exit 1
fi
echo ""

# Step 5: Commit
echo -e "${BLUE}Step 5/6: Creating commit...${NC}"
git commit -m "🎉 Initial commit: Poetry Analyzer App v2.0

Features:
- 100% feature coverage (196/196 features)
- Backend: 20+ analysis services
- Frontend: 17 HTML pages with Toastr notifications
- Multi-language support (7 languages)
- 11 Literary Theory frameworks
- Oulipo constraints
- Information Theory metrics
- Production ready

Based on:
- quantitative_poetry_metrics.md (1261 lines)
- ultimate_literary_master_system.md (841 lines)"

echo -e "${GREEN}✅ Commit created${NC}"
echo ""

# Step 6: Setup remote
echo -e "${BLUE}Step 6/6: Setting up GitHub remote...${NC}"
echo ""
echo "Please create a repository on GitHub first:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: poetry-analyzer-app"
echo "3. Description: Comprehensive Poetry & Literary Analysis System"
echo "4. Public or Private (your choice)"
echo "5. DO NOT initialize with README/.gitignore/license"
echo "6. Click 'Create repository'"
echo ""
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}❌ Username cannot be empty${NC}"
    exit 1
fi

# Remove existing remote if exists
git remote remove origin 2>/dev/null || true

# Add new remote
git remote add origin https://github.com/${GITHUB_USER}/poetry-analyzer-app.git
echo -e "${GREEN}✅ Remote added: https://github.com/${GITHUB_USER}/poetry-analyzer-app.git${NC}"
echo ""

# Rename branch to main
git branch -M main
echo -e "${GREEN}✅ Branch renamed to 'main'${NC}"
echo ""

# Push to GitHub
echo -e "${BLUE}🚀 Pushing to GitHub...${NC}"
echo "You'll be prompted for GitHub credentials..."
echo ""
git push -u origin main

echo ""
echo "=========================================="
echo -e "${GREEN}✅ SUCCESS!${NC}"
echo "=========================================="
echo ""
echo "📦 Your repository is now live at:"
echo "👉 https://github.com/${GITHUB_USER}/poetry-analyzer-app"
echo ""
echo "Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add repository topics: poetry, nlp, literary-analysis, fastapi"
echo "3. Update README with badges and features"
echo "4. Share with the world! 🎉"
echo ""
