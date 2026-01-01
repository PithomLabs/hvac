#!/bin/bash
# Helper script to version prompts before editing
# Usage: ./version_and_edit.sh <prompt_filename>

PROMPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <prompt_filename>"
    echo "Example: $0 chat_system.txt"
    exit 1
fi

# Version the prompt files
python3 "$PROMPTS_DIR/version_prompts.py"

echo ""
echo "✓ Prompt files versioned. You can now safely modify: $1"
