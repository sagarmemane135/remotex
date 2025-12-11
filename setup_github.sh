#!/bin/bash
# RemoteX - GitHub Publishing Setup Script

set -e

echo "🚀 RemoteX GitHub Publishing Setup"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get user input
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your security/contact email: " SECURITY_EMAIL

echo ""
echo "Updating placeholders..."

# Replace YOUR_USERNAME
find . -type f \( -name "*.md" -o -name "*.yml" \) \
  -not -path "*/venv/*" \
  -not -path "*/.git/*" \
  -exec sed -i "s/YOUR_USERNAME/$GITHUB_USER/g" {} +

# Replace YOUR_SECURITY_EMAIL
find . -type f -name "*.md" \
  -not -path "*/venv/*" \
  -not -path "*/.git/*" \
  -exec sed -i "s/YOUR_SECURITY_EMAIL/$SECURITY_EMAIL/g" {} +

# Replace ORIGINAL_OWNER (for upstream)
find . -type f -name "*.md" \
  -not -path "*/venv/*" \
  -not -path "*/.git/*" \
  -exec sed -i "s/ORIGINAL_OWNER/$GITHUB_USER/g" {} +

echo -e "${GREEN}✓ Placeholders updated${NC}"

# Initialize git if not already done
if [ ! -d .git ]; then
    echo ""
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: RemoteX v1.0.0

- High-performance SSH management CLI
- 17 commands for DevOps workflows
- Parallel execution with 5x speedup
- Beautiful Rich-formatted output
- Comprehensive documentation
"
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${YELLOW}! Git repository already exists${NC}"
fi

# Create .gitattributes for better GitHub language detection
cat > .gitattributes << EOF
*.py linguist-language=Python
*.md linguist-documentation
docs/* linguist-documentation
EOF

git add .gitattributes

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "==========="
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo "   Repository name: remotex"
echo "   Description: High-Performance SSH Management CLI for DevOps Engineers"
echo "   Public repository"
echo "   DO NOT initialize with README, license, or .gitignore"
echo ""
echo "2. Push to GitHub:"
echo "   git remote add origin https://github.com/$GITHUB_USER/remotex.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Create a release:"
echo "   git tag -a v1.0.0 -m 'Release v1.0.0 - Initial Production Release'"
echo "   git push origin v1.0.0"
echo "   Then create release on GitHub: https://github.com/$GITHUB_USER/remotex/releases/new"
echo ""
echo "4. Configure repository:"
echo "   - Add topics: python, ssh, devops, cli, typer, paramiko"
echo "   - Enable Issues, Discussions"
echo "   - Set up branch protection for main"
echo ""
echo "See RELEASE_CHECKLIST.md for detailed instructions."
echo ""
echo -e "${GREEN}Good luck with your open source project! 🎉${NC}"
