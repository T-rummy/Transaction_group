#!/bin/bash
# Build script for deployment

echo "Installing dependencies..."
pip install --upgrade pip
pip install setuptools==68.2.2
pip install -r requirements.txt

echo "Build completed successfully!" 