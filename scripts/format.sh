#!/bin/bash

set -e

echo "🎨 Formatting code with black..."
uv run black .

echo "🔧 Auto-fixing with ruff..."
uv run ruff check --fix .

echo "✅ Code formatting complete!"