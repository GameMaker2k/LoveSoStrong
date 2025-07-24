#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import re
import sys
import json
from collections import OrderedDict

def parse_archive(content):
    """Properly parse the archive format maintaining all hierarchical data"""
    data = OrderedDict()
    stack = []
    current = data
    current_section = None
    current_key = None
    body_mode = False
    body_content = []
    body_name = None
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.rstrip()
        
        # Check for section markers
        start_match = re.match(r'^--- Start (.*) ---$', line)
        end_match = re.match(r'^--- End (.*) ---$', line)
        
        if start_match:
            section_name = start_match.group(1)
            
            # Handle body sections
            if 'Body' in section_name:
                body_mode = True
                body_name = section_name.replace(' Body', '')
                body_content = []
                continue
            
            # Create new section container
            new_section = OrderedDict()
            if current_section is None:
                # Top-level section
                if section_name not in data:
                    data[section_name] = []
                data[section_name].append(new_section)
            else:
                # Nested section
                if current_section not in current:
                    current[current_section] = []
                current[current_section].append(new_section)
            
            # Push current context to stack
            stack.append((current, current_section))
            current = new_section
            current_section = None
            continue
            
        if end_match:
            section_name = end_match.group(1)
            
            # Handle body sections
            if 'Body' in section_name:
                body_mode = False
                if body_name and body_content:
                    # Remove trailing empty lines
                    while body_content and not body_content[-1].strip():
                        body_content.pop()
                    current[body_name] = '\n'.join(body_content)
                body_name = None
                body_content = []
                continue
            
            # Pop context from stack
            if stack:
                current, current_section = stack.pop()
            continue
            
        # Handle body content
        if body_mode:
            body_content.append(line)
            continue
            
        # Handle key-value pairs
        if ': ' in line:
            key, value = line.split(': ', 1)
            current_key = key
            current_section = None
            current[key] = value
        elif line.endswith(':'):
            current_key = line[:-1]
            current_section = None
            current[current_key] = ''
        elif current_key and line.strip():
            # Append to previous value
            current[current_key] += '\n' + line
        elif line.strip():
            # Potential section name without key-value pair
            current_section = line.strip()
    
    return data

def generate_archive(data):
    """Generate the archive format from the structured data"""
    output = []
    
    def process_section(section, name):
        output.append('--- Start {} ---'.format(name))
        
        for key, value in section.items():
            if isinstance(value, OrderedDict):
                process_section(value, key)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, (OrderedDict, dict)):
                        process_section(item, key)
                    else:
                        output.append('{}: {}'.format(key, item))
            elif '\n' in str(value):
                output.append('{}:'.format(key))
                output.append('--- Start {} Body ---'.format(key))
                output.append(value)
                output.append('--- End {} Body ---'.format(key))
            else:
                output.append('{}: {}'.format(key, value))
        
        output.append('--- End {} ---'.format(name))
    
    for section_name, section_data in data.items():
        if isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, (OrderedDict, dict)):
                    process_section(item, section_name)
                else:
                    output.append('{}: {}'.format(section_name, item))
        else:
            process_section(section_data, section_name)
    
    return '\n'.join(output)

# JSON support functions
def to_json(data, indent=None):
    """Convert the parsed data to JSON string"""
    def convert(obj):
        if isinstance(obj, OrderedDict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        return obj
    return json.dumps(convert(data), indent=indent, ensure_ascii=False)

def from_json(json_str):
    """Convert JSON string back to archive structure"""
    def convert(obj):
        if isinstance(obj, dict):
            return OrderedDict((k, convert(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        return obj
    return convert(json.loads(json_str))

def main():
    # Example usage
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    # Parse the archive
    parsed_data = parse_archive(content)
    
    # Convert to JSON
    json_str = to_json(parsed_data, indent=2)
    print("\nJSON Representation:")
    print(json_str)
    
    # Convert back from JSON
    reconstructed_data = from_json(json_str)
    
    # Regenerate archive format
    regenerated = generate_archive(reconstructed_data)
    
    # Verify round trip
    print("\nOriginal == Regenerated?", content.strip() == regenerated.strip())
    
    # Example access
    if 'User List' in parsed_data:
        print("\nUsers:")
        for user in parsed_data['User List']:
            print("- {} (@{})".format(user.get('Name', ''), user.get('Handle', '')))
    
    if 'Message List' in parsed_data:
        print("\nThreads:")
        for thread in parsed_data['Message List']:
            print("- {} ({} posts)".format(thread.get('Title', ''), 
                  len([k for k in thread.keys() if k.startswith('Post')])))

if __name__ == '__main__':
    main()
