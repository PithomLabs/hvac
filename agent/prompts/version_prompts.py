#!/usr/bin/env python3
"""
Automatic versioning utility for prompt files.
This script creates versioned backups of prompt files before they are modified.
"""

import os
import shutil
import re

PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def get_next_version(base_filename):
    """Find the next version number for a given prompt file."""
    basename = base_filename.replace('.txt', '')
    existing_versions = []
    
    for filename in os.listdir(PROMPTS_DIR):
        # Match pattern like chat_system_v10.txt
        match = re.match(rf'{re.escape(basename)}_v(\d+)\.txt$', filename)
        if match:
            existing_versions.append(int(match.group(1)))
    
    return max(existing_versions) + 1 if existing_versions else 1


def version_prompt_file(filename):
    """
    Create a versioned backup of a prompt file.
    
    Args:
        filename: Base filename like 'chat_system.txt'
    
    Returns:
        Path to the versioned file
    """
    source_path = os.path.join(PROMPTS_DIR, filename)
    
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Prompt file not found: {source_path}")
    
    # Get next version number
    version_num = get_next_version(filename)
    
    # Create versioned filename
    basename = filename.replace('.txt', '')
    versioned_filename = f"{basename}_v{version_num}.txt"
    versioned_path = os.path.join(PROMPTS_DIR, versioned_filename)
    
    # Copy current file to versioned backup
    shutil.copy2(source_path, versioned_path)
    
    print(f"✓ Versioned: {filename} → {versioned_filename}")
    return versioned_path


def version_all_prompts():
    """Version all prompt files in the prompts directory."""
    prompt_files = ['chat_system.txt', 'decide_system.txt', 'extract_system.txt', 'chat_examples.txt']
    
    versioned_files = []
    for filename in prompt_files:
        filepath = os.path.join(PROMPTS_DIR, filename)
        if os.path.exists(filepath):
            versioned_path = version_prompt_file(filename)
            versioned_files.append(versioned_path)
    
    return versioned_files


if __name__ == "__main__":
    print("Versioning all prompt files...")
    versioned = version_all_prompts()
    print(f"\n✓ Created {len(versioned)} versioned backup(s)")
