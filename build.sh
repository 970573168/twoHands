#!/bin/bash
set -e

# 构建 Lambda 部署包
BUILD_DIR="build"
LAMBDA_DIR="src"
PACKAGE_FILE="lambda.zip"

echo "🧹 Cleaning build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "📦 Installing dependencies..."
pip install -r requirements.txt -t "$BUILD_DIR" --platform manylinux2014_aarch64 --only-binary=:all: --python-version 3.12

echo "📋 Copying Lambda function..."
cp "$LAMBDA_DIR/lambda_function.py" "$BUILD_DIR/"

echo "🗜️ Creating deployment package..."
cd "$BUILD_DIR"
zip -r9 "../$PACKAGE_FILE" .
cd ..

echo "✅ Build complete: $PACKAGE_FILE"
echo "📊 Package size: $(du -h $PACKAGE_FILE | cut -f1)"
