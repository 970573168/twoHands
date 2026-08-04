#!/bin/bash
set -euo pipefail

# ==============================
# Lambda Build Script
# ==============================

BUILD_DIR="build"
LAMBDA_DIR="src"
PACKAGE_FILE="lambda.zip"

echo "=========================================="
echo "🔨 Lambda build started"
echo "=========================================="

echo "Working directory: $(pwd)"
echo "Python version:"
python --version || true
echo "Pip version:"
pip --version || true

echo ""
echo "🧹 Cleaning build directory and old package..."
rm -rf "$BUILD_DIR"
rm -f "$PACKAGE_FILE"
mkdir -p "$BUILD_DIR"

echo ""
echo "🔍 Checking source directory..."
if [ ! -d "$LAMBDA_DIR" ]; then
  echo "❌ Source directory not found: $LAMBDA_DIR"
  exit 1
fi

echo "Source Python files:"
find "$LAMBDA_DIR" -maxdepth 3 -name "*.py" -type f | sort

echo ""
echo "🔍 Checking latest auction code in source..."
grep -n "AUCTION_ABATCH" "$LAMBDA_DIR/yahoo_auction_scraper.py" || {
  echo "❌ AUCTION_ABATCH not found in $LAMBDA_DIR"
  echo "说明 src 目录里的代码不是你以为的最新代码，或者你改的文件不在 src 目录。"
  exit 1
}

grep -n 'params\["abatch"\]' "$LAMBDA_DIR/yahoo_auction_scraper.py" || {
  echo "❌ params[\"abatch\"] not found in $LAMBDA_DIR"
  echo "说明 src 目录里的代码没有 params[\"abatch\"] = AUCTION_ABATCH"
  exit 1
}

if grep -n '_ai_state' "$LAMBDA_DIR/auction_analyzer.py"; then
  echo "❌ auction_analyzer.py still contains removed cross-batch AI state"
  exit 1
fi

echo ""
echo "🧪 Running countdown scheduler tests..."
python -m unittest tests.test_catalog_scanner

echo ""
echo "📦 Installing dependencies into build directory..."
pip install -r requirements.txt -t "$BUILD_DIR" \
  --platform manylinux2014_aarch64 \
  --only-binary=:all: \
  --python-version 3.12

echo ""
echo "📋 Copying Lambda source files..."
cp "$LAMBDA_DIR"/*.py "$BUILD_DIR/"

echo ""
echo "🔍 Checking copied files in build directory..."
find "$BUILD_DIR" -maxdepth 2 -name "*.py" -type f | sort

grep -n "AUCTION_ABATCH" "$BUILD_DIR/yahoo_auction_scraper.py" || {
  echo "❌ AUCTION_ABATCH not found in build directory"
  exit 1
}

grep -n 'params\["abatch"\]' "$BUILD_DIR/yahoo_auction_scraper.py" || {
  echo "❌ params[\"abatch\"] not found in build directory"
  exit 1
}

if grep -n '_ai_state' "$BUILD_DIR/auction_analyzer.py"; then
  echo "❌ Copied auction_analyzer.py contains removed cross-batch AI state"
  exit 1
fi

echo ""
echo "🗜️ Creating deployment package..."
cd "$BUILD_DIR"
zip -r9 "../$PACKAGE_FILE" .
cd ..

echo ""
echo "🔍 Checking generated lambda.zip..."
if [ ! -f "$PACKAGE_FILE" ]; then
  echo "❌ $PACKAGE_FILE was not created"
  exit 1
fi

ls -lh "$PACKAGE_FILE"

rm -rf /tmp/lambda-check
mkdir -p /tmp/lambda-check
unzip -q "$PACKAGE_FILE" -d /tmp/lambda-check

echo ""
echo "📂 Files inside lambda.zip:"
find /tmp/lambda-check -maxdepth 2 -name "*.py" -type f | sort

echo ""
echo "🔍 Verifying latest code inside lambda.zip..."
grep -n "AUCTION_ABATCH" /tmp/lambda-check/yahoo_auction_scraper.py || {
  echo "❌ AUCTION_ABATCH not found inside lambda.zip"
  exit 1
}

grep -n 'params\["abatch"\]' /tmp/lambda-check/yahoo_auction_scraper.py || {
  echo "❌ params[\"abatch\"] not found inside lambda.zip"
  exit 1
}

if grep -n '_ai_state' /tmp/lambda-check/auction_analyzer.py; then
  echo "❌ Packaged auction_analyzer.py contains removed cross-batch AI state"
  exit 1
fi

echo ""
echo "🔐 Calculating local CodeSha256..."
LOCAL_CODE_SHA=$(openssl dgst -sha256 -binary "$PACKAGE_FILE" | openssl base64)
echo "Local lambda.zip CodeSha256: $LOCAL_CODE_SHA"

echo ""
echo "✅ Build complete: $PACKAGE_FILE"
echo "📊 Package size: $(du -h "$PACKAGE_FILE" | cut -f1)"
echo "=========================================="
