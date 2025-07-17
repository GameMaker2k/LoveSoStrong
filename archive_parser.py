#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import argparse
import json
import io
import gzip
import os
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def open_text_file(filepath):
    if filepath.endswith(".gz"):
        return gzip.open(filepath, 'rt')
    else:
        return io.open(filepath, 'r', encoding='utf-8')

# API: Service constructor and add helpers

def init_empty_service(entry, service_name, time_zone="UTC", info=''):
    return {
        'Entry': entry,
        'Service': service_name,
        'TimeZone': time_zone,
        'Users': {},
        'MessageThreads': [],
        'Categories': [],
        'Interactions': [],
        'Categorization': {},
        'Info': info,
    }

def add_user(service, user_id, field_dict):
    service['Users'][user_id] = field_dict

def add_category(service, cat_dict):
    service['Categories'].append(cat_dict)
    t = cat_dict.get('Type')
    l = cat_dict.get('Level')
    if t and t not in service['Categorization']:
        service['Categorization'][t] = []
    if l and l not in service['Categorization'].get(t, []):
        service['Categorization'][t].append(l)

def add_message_thread(service, thread_dict):
    service['MessageThreads'].append(thread_dict)

def add_message_post(thread, message_dict):
    thread['Messages'].append(message_dict)

# Parser using the structure

def parse_txt_archive(filepath):
    service = init_empty_service("default-entry", "MessageBoard", "UTC", "")

    with open_text_file(filepath) as f:
        lines = f.readlines()

    current_section = None
    user = {}
    category = {}
    thread = {}
    message = {}

    for line in lines:
        line = line.strip()

        if line.startswith("--- Start Info Body ---"):
            current_section = "info"
            continue
        elif line.startswith("--- End Info Body ---"):
            current_section = None
            continue
        elif line.startswith("--- Start User Info ---"):
            user = {}
            current_section = "user"
            continue
        elif line.startswith("--- End User Info ---"):
            add_user(service, user.get("ID", "unknown_{}".format(len(service["Users"]))), user)
            user = {}
            current_section = None
            continue
        elif line.startswith("--- Start Bio Body ---"):
            current_section = "user_bio"
            user["Bio"] = ""
            continue
        elif line.startswith("--- End Bio Body ---"):
            current_section = "user"
            continue
        elif line.startswith("--- Start Category List ---"):
            category = {}
            current_section = "category"
            continue
        elif line.startswith("--- End Category List ---"):
            add_category(service, category)
            category = {}
            current_section = None
            continue
        elif line.startswith("--- Start Description Body ---"):
            current_section = "category_desc"
            category["Description"] = ""
            continue
        elif line.startswith("--- End Description Body ---"):
            current_section = "category"
            continue
        elif line.startswith("--- Start Message Thread ---"):
            thread = {"Messages": []}
            current_section = "thread"
            continue
        elif line.startswith("--- End Message Thread ---"):
            add_message_thread(service, thread)
            thread = {}
            current_section = None
            continue
        elif line.startswith("--- Start Message Post ---"):
            message = {}
            current_section = "message"
            continue
        elif line.startswith("--- End Message Post ---"):
            add_message_post(thread, message)
            message = {}
            current_section = "thread"
            continue
        elif line.startswith("--- Start Message Body ---"):
            current_section = "message_body"
            message["Message"] = ""
            continue
        elif line.startswith("--- End Message Body ---"):
            current_section = "message"
            continue

        if current_section == "info":
            service["Info"] += line + "\n"
        elif current_section == "user":
            if ":" in line:
                k, v = line.split(":", 1)
                user[k.strip()] = v.strip()
        elif current_section == "user_bio":
            user["Bio"] += line + "\n"
        elif current_section == "category":
            if ":" in line:
                k, v = line.split(":", 1)
                category[k.strip()] = v.strip()
        elif current_section == "category_desc":
            category["Description"] += line + "\n"
        elif current_section == "thread":
            if ":" in line:
                k, v = line.split(":", 1)
                thread[k.strip()] = v.strip()
        elif current_section == "message":
            if ":" in line:
                k, v = line.split(":", 1)
                message[k.strip()] = v.strip()
        elif current_section == "message_body":
            message["Message"] += line + "\n"

    return service

def save_json(data, out_path):
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2)
    print("[✔] Saved JSON to {}".format(out_path))

def save_yaml(data, out_path):
    if not HAS_YAML:
        print("[!] PyYAML not installed. Skipping YAML export.")
        return
    with open(out_path, 'w') as f:
        yaml.dump(data, f, allow_unicode=True)
    print("[✔] Saved YAML to {}".format(out_path))

def main():
    parser = argparse.ArgumentParser(description="Minimal parser with service structure API.")
    parser.add_argument("input", help="Input archive .txt or .gz file")
    parser.add_argument("--json", default="out.json", help="Output JSON file")
    parser.add_argument("--yaml", default="out.yaml", help="Output YAML file")
    parser.add_argument("--print", action="store_true", help="Print parsed service data")
    args = parser.parse_args()

    service = parse_txt_archive(args.input)

    if args.print:
        print(json.dumps(service, indent=2))

    save_json(service, args.json)
    if HAS_YAML:
        save_yaml(service, args.yaml)

if __name__ == "__main__":
    main()
