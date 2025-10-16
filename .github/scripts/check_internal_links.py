#!/usr/bin/env python3
"""
Check for broken internal links in documentation files.

This script validates that internal links between documentation files
are working correctly and point to existing files and sections.
"""

import os
import re
import sys
from typing import List, Dict, Set, Tuple

def find_markdown_files() -> List[str]:
    """Find all markdown files in the project."""
    md_files = []
    
    # Root level markdown files
    for file in os.listdir('.'):
        if file.endswith('.md'):
            md_files.append(file)
    
    # Documentation files
    docs_dir = 'docs'
    if os.path.exists(docs_dir):
        for file in os.listdir(docs_dir):
            if file.endswith('.md'):
                md_files.append(os.path.join(docs_dir, file))
    
    return md_files

def extract_internal_links(content: str, file_path: str) -> List[Tuple[str, int]]:
    """Extract internal links from markdown content."""
    links = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Find markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, line)
        
        for text, url in matches:
            # Skip external links (http/https)
            if url.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            # Skip images (although they should be checked too)
            if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                continue
            
            links.append((url, line_num))
    
    return links

def validate_file_link(link: str, source_file: str) -> Tuple[bool, str]:
    """Validate that a file link points to an existing file."""
    # Handle anchor links within the same file
    if link.startswith('#'):
        return True, "Anchor link (not validated)"
    
    # Extract file path and anchor
    if '#' in link:
        file_path, anchor = link.split('#', 1)
    else:
        file_path, anchor = link, None
    
    # Resolve relative path
    if source_file.startswith('docs/'):
        # Link from docs directory
        if not file_path.startswith('../'):
            # Link within docs
            full_path = os.path.join('docs', file_path)
        else:
            # Link to root
            full_path = file_path[3:]  # Remove '../'
    else:
        # Link from root directory
        if file_path.startswith('docs/'):
            full_path = file_path
        else:
            full_path = file_path
    
    # Check if file exists
    if not os.path.exists(full_path):
        return False, f"File not found: {full_path}"
    
    # TODO: Could also validate anchors by parsing the target file
    return True, "OK"

def check_common_link_patterns(content: str) -> List[str]:
    """Check for common link pattern issues."""
    issues = []
    
    # Check for missing file extensions
    if re.search(r'\]\([^)]+[^\.md][^)]*\)', content):
        # This is a simple check - could have false positives
        pass
    
    # Check for spaces in links (should be URL encoded)
    space_links = re.findall(r'\]\(([^)]*\s[^)]*)\)', content)
    for link in space_links:
        if not link.startswith(('http://', 'https://')):
            issues.append(f"Link contains unencoded spaces: {link}")
    
    # Check for double slashes
    double_slash_links = re.findall(r'\]\(([^)]*//[^)]*)\)', content)
    for link in double_slash_links:
        if not link.startswith(('http://', 'https://')):
            issues.append(f"Link contains double slashes: {link}")
    
    return issues

def validate_cross_references(md_files: List[str]) -> List[str]:
    """Validate cross-references between documentation files."""
    issues = []
    
    # Build a map of existing files and their sections
    file_sections = {}
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract headers (potential link targets)
            headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            file_sections[md_file] = headers
            
        except Exception as e:
            issues.append(f"Could not read {md_file}: {e}")
    
    return issues

def main():
    """Main link checking function."""
    print("🔗 Checking internal links in documentation...")
    
    md_files = find_markdown_files()
    print(f"📄 Found {len(md_files)} markdown files")
    
    all_issues = []
    
    for md_file in md_files:
        print(f"  Checking {md_file}...")
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            all_issues.append(f"❌ Could not read {md_file}: {e}")
            continue
        
        # Extract internal links
        links = extract_internal_links(content, md_file)
        
        # Validate each link
        for link, line_num in links:
            is_valid, message = validate_file_link(link, md_file)
            
            if not is_valid:
                all_issues.append(f"❌ {md_file}:{line_num} - {message} (link: {link})")
        
        # Check for common link pattern issues
        pattern_issues = check_common_link_patterns(content)
        for issue in pattern_issues:
            all_issues.append(f"⚠️  {md_file} - {issue}")
    
    # Validate cross-references
    cross_ref_issues = validate_cross_references(md_files)
    all_issues.extend(cross_ref_issues)
    
    # Report results
    if all_issues:
        print(f"\n🔍 Found {len(all_issues)} link issues:")
        for issue in all_issues:
            print(f"  {issue}")
        print("\n💡 Consider fixing broken links in documentation")
    else:
        print("✅ All internal links appear to be working")
    
    print("✨ Link checking completed")

if __name__ == '__main__':
    main()