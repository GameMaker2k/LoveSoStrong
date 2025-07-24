#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import re
import sys
import json
from collections import OrderedDict

def parse_archive(content):
    """Parse the archive format into a structured 2D array (list of dicts)"""
    data = OrderedDict()
    current_section = None
    current_subsection = None
    current_object = None
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Section detection
        section_start = re.match(r'^--- Start (\w+(?: \w+)*) ---$', line)
        section_end = re.match(r'^--- End (\w+(?: \w+)*) ---$', line)
        
        if section_start:
            section_name = section_start.group(1)
            if section_name not in data:
                data[section_name] = []
            current_section = section_name
            current_subsection = None
            current_object = OrderedDict()
            i += 1
            continue
            
        if section_end:
            if current_object and len(current_object) > 0:
                data[current_section].append(current_object)
            current_section = None
            current_subsection = None
            current_object = None
            i += 1
            continue
            
        # Body content detection
        body_start = re.match(r'^--- Start (\w+(?: \w+)*) Body ---$', line)
        body_end = re.match(r'^--- End (\w+(?: \w+)*) Body ---$', line)
        
        if body_start:
            body_name = body_start.group(1)
            current_subsection = body_name
            body_lines = []
            i += 1
            while i < len(lines):
                if re.match(r'^--- End {} Body ---$'.format(body_name), lines[i].strip()):
                    break
                body_lines.append(lines[i])
                i += 1
            current_object[body_name] = '\n'.join(body_lines)
            i += 1
            continue
            
        if body_end:
            current_subsection = None
            i += 1
            continue
            
        # Key-value pairs
        if current_section and line:
            if ': ' in line:
                key, value = line.split(': ', 1)
                current_object[key] = value
            elif line.endswith(':'):
                key = line[:-1]
                current_object[key] = ''
            elif current_subsection is None:
                if current_object and len(current_object) > 0:
                    last_key = next(reversed(current_object))
                    current_object[last_key] += '\n' + line
        i += 1
    
    return data

def generate_archive(data):
    """Generate the archive format from the structured data"""
    output = []
    
    for section, items in data.items():
        if not items:
            output.append('--- Start {} ---'.format(section))
            output.append('--- End {} ---'.format(section))
            continue
            
        for item in items:
            output.append('--- Start {} ---'.format(section))
            
            for key, value in item.items():
                if isinstance(value, dict):
                    pass
                elif '\n' in str(value):
                    output.append('{}:'.format(key))
                    output.append('--- Start {} Body ---'.format(key))
                    output.append(str(value))
                    output.append('--- End {} Body ---'.format(key))
                else:
                    if value is None:
                        value = ''
                    output.append('{}: {}'.format(key, str(value)))
            
            output.append('--- End {} ---'.format(section))
    
    return '\n'.join(output)

def to_json(data, indent=None):
    """Convert the 2D array structure to JSON string"""
    # Convert OrderedDict to regular dict for JSON serialization
    def convert(data):
        if isinstance(data, OrderedDict):
            return {k: convert(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert(item) for item in data]
        else:
            return data
    
    return json.dumps(convert(data), indent=indent, ensure_ascii=False)

def from_json(json_str):
    """Convert JSON string back to 2D array structure"""
    def convert(data):
        if isinstance(data, dict):
            return OrderedDict((k, convert(v)) for k, v in data.items())
        elif isinstance(data, list):
            return [convert(item) for item in data]
        else:
            return data
    
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
