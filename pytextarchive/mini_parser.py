#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import re
import sys
import json
from collections import OrderedDict
import io
import gzip
import bz2
import lzma
import marshal
import pickle
import ast
from typing import Any, Union, TextIO, BinaryIO
from pathlib import Path

# Optional dependencies
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

try:
    import pyzstd
    HAS_PYZSTD = True
except ImportError:
    HAS_PYZSTD = False

try:
    import lzo
    HAS_LZO = True
except ImportError:
    HAS_LZO = False

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

def parse_file(filename, validate_only=False, verbose=False):
    with open_compressed_file(filename) as file:
        lines = file.read()
    return parse_archive(lines)

def parse_string(data, validate_only=False, verbose=False):
    lines = StringIO(data).read()
    return parse_archive(lines)

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

def services_to_string(services):
    return generate_archive(services)

def save_services_to_file(services, filename, line_ending='lf'):
    """
    Save services to a file, inferring compression by extension (Python 2/3 compatible).
    """
    data = generate_archive(services)
    save_compressed_file(data, filename)

class CompressionError(Exception):
    """Custom exception for compression-related errors"""
    pass

def open_compressed_file(filename: Union[str, Path], mode: str = 'rt', encoding: str = 'utf-8') -> Union[TextIO, BinaryIO]:
    """
    Open a file with automatic decompression based on extension.
    
    Args:
        filename: Path to the file
        mode: File mode ('r', 'w', 'rt', 'wb', etc.)
        encoding: Text encoding for text modes
        
    Returns:
        File-like object
        
    Raises:
        CompressionError: If compression method is not available
        ValueError: For invalid mode/extension combinations
    """
    filename = str(filename)
    
    if 'r' in mode:
        if filename.endswith('.gz'):
            return gzip.open(filename, mode, encoding=encoding)
        elif filename.endswith('.bz2'):
            return bz2.open(filename, mode, encoding=encoding)
        elif filename.endswith(('.xz', '.lzma')):
            return lzma.open(filename, mode, encoding=encoding)
        elif filename.endswith('.zst'):
            if HAS_ZSTD:
                fh = open(filename, 'rb')
                dctx = zstd.ZstdDecompressor()
                return dctx.stream_reader(fh)
            elif HAS_PYZSTD:
                return pyzstd.ZstdFile(filename, mode)
            else:
                raise CompressionError("zstandard decompression not available")
        elif filename.endswith('.lzo') and HAS_LZO:
            with open(filename, 'rb') as f:
                decompressed = lzo.decompress(f.read())
                return io.StringIO(decompressed.decode(encoding))
        else:
            return open(filename, mode, encoding=encoding)
    
    elif 'w' in mode:
        if filename.endswith('.gz'):
            return gzip.open(filename, mode, encoding=encoding)
        elif filename.endswith('.bz2'):
            return bz2.open(filename, mode, encoding=encoding)
        elif filename.endswith(('.xz', '.lzma')):
            return lzma.open(filename, mode, encoding=encoding)
        elif filename.endswith('.zst'):
            if HAS_ZSTD:
                fh = open(filename, 'wb')
                cctx = zstd.ZstdCompressor()
                return cctx.stream_writer(fh)
            elif HAS_PYZSTD:
                return pyzstd.ZstdFile(filename, mode)
            else:
                raise CompressionError("zstandard compression not available")
        elif filename.endswith('.lzo') and HAS_LZO:
            # LZO doesn't have native streaming compression in Python
            # We'll handle this in save_compressed_file instead
            raise CompressionError("LZO compression must use save_compressed_file")
        else:
            return open(filename, mode, encoding=encoding)
    
    else:
        raise ValueError(f"Unsupported mode: {mode}")

def save_compressed_file(data: Union[str, bytes], filename: Union[str, Path], mode: str = 'wt', encoding: str = 'utf-8') -> None:
    """
    Save data to a file with automatic compression based on extension.
    
    Args:
        data: Data to save (str or bytes)
        filename: Path to save to
        mode: File mode ('w', 'wb', 'wt', etc.)
        encoding: Text encoding for text modes
        
    Raises:
        CompressionError: If compression method is not available
        ValueError: For invalid data/mode combinations
    """
    filename = str(filename)
    
    if isinstance(data, str) and 'b' in mode:
        raise ValueError("Cannot write text data in binary mode")
    if isinstance(data, bytes) and 't' in mode:
        raise ValueError("Cannot write binary data in text mode")
    
    if filename.endswith('.lzo') and HAS_LZO:
        # Special handling for LZO since it doesn't have streaming compression
        if isinstance(data, str):
            data = data.encode(encoding)
        compressed = lzo.compress(data)
        with open(filename, 'wb') as f:
            f.write(compressed)
        return
    
    with open_compressed_file(filename, mode, encoding) as f:
        if isinstance(data, bytes) and 't' not in mode:
            f.write(data)
        else:
            if isinstance(data, bytes):
                data = data.decode(encoding)
            f.write(data)

# Serialization functions with improved type hints and error handling

def to_json(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """Convert data to a JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

def from_json(json_str: str) -> Any:
    """Convert a JSON string back to Python data."""
    return json.loads(json_str)

def load_from_json_file(filename: Union[str, Path]) -> Any:
    """Load data from a JSON file."""
    with open_compressed_file(filename, 'rt', encoding='utf-8') as file:
        return json.load(file)

def save_to_json_file(data: Any, filename: Union[str, Path], indent: int = 2, ensure_ascii: bool = False) -> None:
    """Save data to a JSON file."""
    json_data = to_json(data, indent, ensure_ascii)
    save_compressed_file(json_data, filename)

def to_yaml(data: Any) -> Union[str, bool]:
    """Convert data to a YAML string if PyYAML is available."""
    if not HAS_YAML:
        return False
    return yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

def from_yaml(yaml_str: str) -> Union[Any, bool]:
    """Convert a YAML string to Python data if PyYAML is available."""
    if not HAS_YAML:
        return False
    return yaml.safe_load(yaml_str)

def load_from_yaml_file(filename: Union[str, Path]) -> Union[Any, bool]:
    """Load data from a YAML file if PyYAML is available."""
    if not HAS_YAML:
        return False
    with open_compressed_file(filename, 'rt', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_to_yaml_file(data: Any, filename: Union[str, Path]) -> bool:
    """Save data to a YAML file if PyYAML is available."""
    if not HAS_YAML:
        return False
    yaml_data = to_yaml(data)
    if yaml_data is False:
        return False
    save_compressed_file(yaml_data, filename)
    return True

def to_marshal(data: Any) -> bytes:
    """Convert data to a marshaled byte string."""
    return marshal.dumps(data)

def from_marshal(marshal_bytes: bytes) -> Any:
    """Convert a marshaled byte string back to Python data."""
    return marshal.loads(marshal_bytes)

def load_from_marshal_file(filename: Union[str, Path]) -> Any:
    """Load data from a marshal file."""
    with open_compressed_file(filename, 'rb') as file:
        return marshal.load(file)

def save_to_marshal_file(data: Any, filename: Union[str, Path]) -> None:
    """Save data to a marshal file."""
    marshal_data = to_marshal(data)
    save_compressed_file(marshal_data, filename, 'wb')

def to_pickle(data: Any, protocol: int = pickle.HIGHEST_PROTOCOL) -> bytes:
    """Convert data to a pickled byte string."""
    return pickle.dumps(data, protocol=protocol)

def from_pickle(pickle_bytes: bytes) -> Any:
    """Convert a pickled byte string back to Python data."""
    return pickle.loads(pickle_bytes)

def load_from_pickle_file(filename: Union[str, Path]) -> Any:
    """Load data from a pickle file."""
    with open_compressed_file(filename, 'rb') as file:
        return pickle.load(file)

def save_to_pickle_file(data: Any, filename: Union[str, Path], protocol: int = pickle.HIGHEST_PROTOCOL) -> None:
    """Save data to a pickle file."""
    pickle_data = to_pickle(data, protocol)
    save_compressed_file(pickle_data, filename, 'wb')

def to_array(data: Any) -> str:
    """Convert data to a string representation using Python literal syntax."""
    return repr(data)

def from_array(data_str: str) -> Any:
    """Convert a string (Python literal) back to data using safe evaluation."""
    return ast.literal_eval(data_str)

def load_from_array_file(filename: Union[str, Path]) -> Any:
    """Load data from a file containing Python literal syntax."""
    with open_compressed_file(filename, 'rt', encoding='utf-8') as file:
        return ast.literal_eval(file.read())

def save_to_array_file(data: Any, filename: Union[str, Path]) -> None:
    """Save data to a file using Python literal syntax."""
    data_str = to_array(data)
    save_compressed_file(data_str, filename)

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
