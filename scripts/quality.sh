#!/bin/bash

set -e

echo "🔍 Running code quality checks..."

echo "📋 Running ruff linter..."
uv run ruff check .

echo "🎨 Running black formatter check..."
uv run black --check --diff .

echo "✅ All quality checks passed!"