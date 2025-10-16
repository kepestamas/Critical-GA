#!/usr/bin/env python3
"""
Validate code examples in README.md to ensure they are accurate and up-to-date.

This script extracts code blocks from the README and validates that they
represent accurate usage of the actual codebase.
"""

import re
import os
import sys
from typing import List, Dict, Tuple

def extract_code_blocks(markdown_content: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown content."""
    code_blocks = []
    
    # Pattern to match code blocks with optional language specification
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    
    for language, code in matches:
        if language in ['bash', 'python', ''] or not language:
            code_blocks.append({
                'language': language or 'unknown',
                'code': code.strip()
            })
    
    return code_blocks

def validate_command_examples(code_blocks: List[Dict[str, str]]) -> List[str]:
    """Validate command-line examples in code blocks."""
    issues = []
    
    for block in code_blocks:
        if block['language'] == 'bash' or 'python ' in block['code']:
            lines = block['code'].split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('python '):
                    # Extract the command
                    command_parts = line.split()
                    if len(command_parts) >= 2:
                        script_name = command_parts[1]
                        
                        # Check if script exists
                        if not os.path.exists(script_name):
                            issues.append(f"Script referenced in README not found: {script_name}")
                        
                        # Validate parameter count for known scripts
                        if script_name == 'connectivity_ga.py' and len(command_parts) != 10:
                            issues.append(f"GA command has wrong parameter count: {line}")
                        elif script_name == 'connectivity_greedy.py' and len(command_parts) != 4:
                            issues.append(f"Greedy command has wrong parameter count: {line}")
                        elif script_name == 'network_analyzer.py' and len(command_parts) != 3:
                            issues.append(f"Analyzer command has wrong parameter count: {line}")
    
    return issues

def validate_file_references(markdown_content: str) -> List[str]:
    """Validate file references in the README."""
    issues = []
    
    # Find references to files in backticks
    file_pattern = r'`([^`]+\.(py|txt|md|edges|mtx))`'
    file_matches = re.findall(file_pattern, markdown_content)
    
    for file_match, ext in file_matches:
        file_path = file_match
        
        # Skip obvious placeholders or examples
        if any(placeholder in file_path.lower() for placeholder in ['example', 'your_', 'custom_']):
            continue
            
        # Check if file exists
        if not os.path.exists(file_path):
            # Try in inputs directory for data files
            if ext in ['txt', 'edges', 'mtx'] and os.path.exists(f'inputs/{file_path}'):
                continue
            # Try in docs directory for documentation
            elif ext == 'md' and os.path.exists(f'docs/{file_path}'):
                continue
            else:
                issues.append(f"File referenced in README not found: {file_path}")
    
    return issues

def validate_parameter_descriptions(markdown_content: str) -> List[str]:
    """Validate that parameter descriptions match actual usage."""
    issues = []
    
    # Look for parameter description sections
    param_sections = re.findall(r'\*\*Parameters:\*\*(.*?)(?=\n\n|\*\*|$)', markdown_content, re.DOTALL)
    
    for section in param_sections:
        # Check for common parameter naming consistency
        if 'input_file' in section and 'Network file from inputs/' not in section:
            issues.append("Parameter description for input_file may be incomplete")
        
        if 'population_size' in section and 'recommended' not in section.lower():
            issues.append("Population size parameter missing recommended values")
    
    return issues

def check_example_consistency() -> List[str]:
    """Check consistency between different examples in the README."""
    issues = []
    
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all GA command examples
        ga_commands = re.findall(r'python connectivity_ga\.py ([^\n]+)', content)
        
        # Check if examples use consistent parameter ranges
        for cmd in ga_commands:
            parts = cmd.split()
            if len(parts) >= 8:
                try:
                    node_frac = float(parts[2])
                    edge_frac = float(parts[3])
                    pop_size = int(parts[4])
                    
                    if node_frac > 0.2:
                        issues.append(f"Example uses high node removal fraction: {node_frac}")
                    if edge_frac > 0.2:
                        issues.append(f"Example uses high edge removal fraction: {edge_frac}")
                    if pop_size > 200:
                        issues.append(f"Example uses very high population size: {pop_size}")
                        
                except ValueError:
                    issues.append(f"Invalid parameter values in example: {cmd}")
    
    except FileNotFoundError:
        issues.append("README.md not found")
    
    return issues

def main():
    """Main README validation function."""
    print("📖 Validating README.md examples...")
    
    if not os.path.exists('README.md'):
        print("❌ README.md not found")
        sys.exit(1)
    
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()
    except Exception as e:
        print(f"❌ Error reading README.md: {e}")
        sys.exit(1)
    
    all_issues = []
    
    # Extract and validate code blocks
    code_blocks = extract_code_blocks(readme_content)
    print(f"📄 Found {len(code_blocks)} code blocks")
    
    # Validate command examples
    command_issues = validate_command_examples(code_blocks)
    all_issues.extend(command_issues)
    
    # Validate file references
    file_issues = validate_file_references(readme_content)
    all_issues.extend(file_issues)
    
    # Validate parameter descriptions
    param_issues = validate_parameter_descriptions(readme_content)
    all_issues.extend(param_issues)
    
    # Check example consistency
    consistency_issues = check_example_consistency()
    all_issues.extend(consistency_issues)
    
    # Report results
    if all_issues:
        print(f"\n⚠️  Found {len(all_issues)} potential issues:")
        for issue in all_issues:
            print(f"  • {issue}")
        print("\n💡 Consider updating the README.md examples")
    else:
        print("✅ README.md examples appear to be valid")
    
    print("✨ README validation completed")

if __name__ == '__main__':
    main()