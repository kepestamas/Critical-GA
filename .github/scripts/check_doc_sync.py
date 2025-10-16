#!/usr/bin/env python3
"""
Check if documentation updates are needed when code changes are detected.

This script analyzes the git diff and determines if documentation files
need to be updated based on the types of changes made to the codebase.
"""

import subprocess
import sys
import os
from typing import List, Set, Dict
import re

def get_changed_files() -> List[str]:
    """Get list of files changed in the current commit/PR."""
    try:
        # Try to get changed files from git diff
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            return result.stdout.strip().split('\n')
        
        # Fallback: check staged files
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    except subprocess.CalledProcessError:
        print("Warning: Could not determine changed files")
        return []

def analyze_function_changes(file_path: str) -> Dict[str, List[str]]:
    """Analyze Python file for function signature changes."""
    if not file_path.endswith('.py') or not os.path.exists(file_path):
        return {}
    
    changes = {
        'new_functions': [],
        'modified_functions': [],
        'deleted_functions': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find function definitions
        function_pattern = r'^def\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[^:]+)?:'
        functions = re.findall(function_pattern, content, re.MULTILINE)
        
        # For simplicity, we'll just report that functions exist
        # In a real implementation, you'd compare with previous version
        if functions:
            changes['new_functions'] = functions
            
    except Exception as e:
        print(f"Warning: Could not analyze {file_path}: {e}")
    
    return changes

def check_documentation_files_updated(changed_files: List[str]) -> Dict[str, bool]:
    """Check if relevant documentation files were updated."""
    doc_files = {
        'README.md': False,
        'docs/API.md': False,
        'docs/ALGORITHMS.md': False,
        'docs/DATASETS.md': False,
        'CHANGELOG.md': False
    }
    
    for file in changed_files:
        if file in doc_files:
            doc_files[file] = True
    
    return doc_files

def main():
    """Main documentation sync checker."""
    print("🔍 Checking for documentation sync issues...")
    
    changed_files = get_changed_files()
    if not changed_files:
        print("✅ No changed files detected")
        return
    
    print(f"📁 Changed files: {', '.join(changed_files)}")
    
    # Check for Python file changes
    python_files = [f for f in changed_files if f.endswith('.py')]
    dataset_files = [f for f in changed_files if f.startswith('inputs/')]
    
    doc_status = check_documentation_files_updated(changed_files)
    
    issues = []
    
    # Check if Python files changed but API docs weren't updated
    if python_files and not doc_status['docs/API.md']:
        for py_file in python_files:
            changes = analyze_function_changes(py_file)
            if changes['new_functions'] or changes['modified_functions']:
                issues.append(f"⚠️  {py_file} has function changes but docs/API.md wasn't updated")
    
    # Check if algorithm files changed but algorithm docs weren't updated
    algorithm_files = ['connectivity_ga.py', 'connectivity_greedy.py']
    if any(f in python_files for f in algorithm_files) and not doc_status['docs/ALGORITHMS.md']:
        issues.append("⚠️  Algorithm files changed but docs/ALGORITHMS.md wasn't updated")
    
    # Check if dataset files changed but dataset docs weren't updated
    if dataset_files and not doc_status['docs/DATASETS.md']:
        issues.append("⚠️  Dataset files changed but docs/DATASETS.md wasn't updated")
    
    # Check if any code changed but README wasn't updated (for major changes)
    major_files = ['connectivity_ga.py', 'connectivity_greedy.py', 'network_analyzer.py']
    if any(f in python_files for f in major_files) and not doc_status['README.md']:
        issues.append("ℹ️  Major files changed - consider updating README.md if usage changed")
    
    # Check if any files changed but CHANGELOG wasn't updated
    if changed_files and not doc_status['CHANGELOG.md']:
        issues.append("ℹ️  Files changed but CHANGELOG.md wasn't updated")
    
    # Report results
    if issues:
        print("\n📋 Documentation sync issues found:")
        for issue in issues:
            print(issue)
        print("\n💡 Consider updating the relevant documentation files.")
    else:
        print("✅ Documentation appears to be in sync")
    
    # Don't fail the build for documentation warnings
    print("\n✨ Documentation check completed")

if __name__ == '__main__':
    main()