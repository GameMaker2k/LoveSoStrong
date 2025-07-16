#!/usr/bin/env bash

# Output directory for generated files
output_dir="./redata"
mkdir -p "$output_dir"

echo "Starting conversion of *_lf.txt files..."

# Loop over all files with the _lf.txt suffix in ./redata
for file in ./redata/*_lf.txt; do
    # Extract just the base name without path or _lf.txt suffix
    base_name="$(basename "${file%_lf.txt}")"

    echo "Processing: $base_name"

    # Define output file paths
    crlf_file="./redata/${base_name}_crlf.txt"
    cr_file="./redata/${base_name}_cr.txt"
    json_file="${output_dir}/${base_name}.json"
    yaml_file="${output_dir}/${base_name}.yaml"
    html_file="${output_dir}/${base_name}.html"

    # Create CRLF and CR versions of the input file
    unix2dos -n "$file" "$crlf_file" && echo "  ➤ Created: $crlf_file"
    unix2mac -n "$file" "$cr_file" && echo "  ➤ Created: $cr_file"

    # Convert to JSON if it doesn't already exist
    if [ ! -f "$json_file" ]; then
        python3 ./display_message_file.py "$file" --to-json "$json_file" \
          && echo "  ✅ JSON saved to $json_file" \
          || echo "  ❌ Failed to convert $file to JSON"
    else
        echo "  ⏩ JSON already exists: $json_file"
    fi

    # Convert to YAML
    if [ ! -f "$yaml_file" ]; then
        python3 ./display_message_file.py "$file" --to-yaml "$yaml_file" \
          && echo "  ✅ YAML saved to $yaml_file" \
          || echo "  ❌ Failed to convert $file to YAML"
    else
        echo "  ⏩ YAML already exists: $yaml_file"
    fi

    # Convert to HTML
    if [ ! -f "$html_file" ]; then
        python3 ./display_message_file.py "$file" --to-html "$html_file" \
          && echo "  ✅ HTML saved to $html_file" \
          || echo "  ❌ Failed to convert $file to HTML"
    else
        echo "  ⏩ HTML already exists: $html_file"
    fi

    echo ""
done

echo "✔ All conversions complete. Output saved in: $output_dir"
