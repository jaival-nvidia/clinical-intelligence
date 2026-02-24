#!/usr/bin/env bash
#
# Serve GLM-4.7-Flash locally via Ollama.
# Assumes Ollama is already installed (https://ollama.com).
#

set -euo pipefail

MODEL="glm-4.7-flash"

echo "Pulling ${MODEL} (if not already downloaded)..."
ollama pull "${MODEL}"

echo ""
echo "Model ready. Ollama serves at http://localhost:11434"
echo ""
echo "To test:"
echo "  ollama run ${MODEL} 'Hello'"
echo ""
echo "Claude Code will connect to this automatically if configured."
