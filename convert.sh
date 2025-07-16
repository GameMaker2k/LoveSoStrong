bash ./data/convert.sh

for file in ./data/*_lf.txt; do
    base_name="$(basename "${file%_lf.txt}")"
    org_file="./redata/${base_name}_lf.txt"
    python3 ./display_message_file.py "$file" --to-original "$org_file"
done

bash ./redata/convert.sh
