#!/usr/bin/env bash

# Loop over all files with the _lf.txt suffix
for file in *_lf.txt; do
    # Extract the base name without the _lf.txt suffix
    base_name="${file%_lf.txt}"

    # Convert to CRLF (Windows-style) line endings
    unix2dos -n "$file" "${base_name}_crlf.txt"

    # Convert to CR (Mac-style) line endings
    unix2mac -n "$file" "${base_name}_cr.txt"

    # Convert to JSON file
    python3 ../display_message_file.py "$file" --to-json "${base_name}.json"

    # Convert to YAML file
    python3 ../display_message_file.py "$file" --to-yaml "${base_name}.yaml"

    # Convert to HTML file
    python3 ../display_message_file.py "$file" --to-html "${base_name}.html"
done

echo "Conversion completed!"
