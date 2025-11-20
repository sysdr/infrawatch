#!/bin/bash
echo "Cleaning all caches..."
rm -rf node_modules/.cache
rm -rf .cache
rm -rf build
rm -rf .npm_hash
npm cache clean --force 2>/dev/null
echo "✓ All caches cleared"
echo ""
echo "Current configuration:"
echo "  - Tailwind CSS: $(npm list tailwindcss 2>/dev/null | grep tailwindcss | head -1 | awk '{print $NF}')"
echo "  - PostCSS config: $(test -f postcss.config.js && echo 'exists' || echo 'missing')"
echo ""
echo "Please restart your dev server: npm start"
