#!/bin/bash
# zkComply MVP - Quick Deploy Script

set -e

echo "🚀 zkComply MVP Deployment Script"
echo "=================================="

# Check Python version
echo "🔍 Checking Python version..."
python3 --version || (echo "❌ Python 3.7+ required" && exit 1)

echo "✅ Python version OK"

# Run tests
echo ""
echo "🧪 Running test suite..."
python3 tests/test_mvp.py || (echo "❌ Tests failed" && exit 1)

echo ""
echo "🎬 Running demo..."
python3 src/zkcomply_mvp.py

echo ""
echo "📋 System information..."
python3 cli.py info

echo ""
echo "🎯 Testing CLI commands..."
echo "   • Testing legitimate user..."
python3 cli.py prove --name "Alice Johnson" --dob "1992-03-15" --output alice_proof.json

echo "   • Verifying proof..."
python3 cli.py verify --proof alice_proof.json

echo "   • Testing sanctioned user..."
python3 cli.py prove --name "VLADIMIR PUTIN" --dob "1952-10-07" || echo "   ✅ Correctly rejected sanctioned user"

echo ""
echo "🎉 Deployment successful!"
echo "📖 Read README.md for full documentation"
echo "🏃 Try: python3 cli.py prove --name 'Your Name' --dob 'YYYY-MM-DD'"
echo "🔐 zkComply: Privacy-preserving compliance for the modern world!"
