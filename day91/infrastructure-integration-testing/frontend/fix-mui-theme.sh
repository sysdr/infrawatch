#!/bin/bash
# Fix for MUI useTheme.js missing module error

FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Fixing MUI useTheme.js issue..."

# Create the missing useTheme.js file
mkdir -p "$FRONTEND_DIR/node_modules/@mui/material/styles"

cat > "$FRONTEND_DIR/node_modules/@mui/material/styles/useTheme.js" << 'EOF'
export { default } from '@mui/system/useTheme';
EOF

echo "✓ Created useTheme.js fix"
echo "File location: $FRONTEND_DIR/node_modules/@mui/material/styles/useTheme.js"
