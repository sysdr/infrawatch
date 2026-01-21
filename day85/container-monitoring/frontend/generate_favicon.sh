#!/bin/bash
# Simple script to generate favicon.ico from SVG
# Requires ImageMagick or similar tool

if command -v convert &> /dev/null; then
    convert public/favicon.svg -resize 32x32 public/favicon.ico
    echo "Generated favicon.ico from favicon.svg"
elif command -v magick &> /dev/null; then
    magick public/favicon.svg -resize 32x32 public/favicon.ico
    echo "Generated favicon.ico from favicon.svg"
else
    echo "ImageMagick not found. Using SVG favicon only."
    echo "Modern browsers will use favicon.svg automatically."
fi
