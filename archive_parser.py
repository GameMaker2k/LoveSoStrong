#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import argparse
import json
import re
import os
import sys

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def parse_txt_archive(filepath):
    data = {
        "info": "",
        "users": [],
        "categories": [],
        "forums": [],
        "threads": []
    }

    with open(filepath, 'r') as f:
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
            data["users"].append(user)
            user = {}
            current_section = None
            continue
        elif line.startswith("--- Start Bio Body ---"):
            current_section = "user_bio"
            user["bio"] = ""
            continue
        elif line.startswith("--- End Bio Body ---"):
            current_section = "user"
            continue
        elif line.startswith("--- Start Category List ---"):
            category = {}
            current_section = "category"
            continue
        elif line.startswith("--- End Category List ---"):
            if category.get("Kind") == "Categories":
                data["categories"].append(category)
            elif category.get("Kind") == "Forums":
                data["forums"].append(category)
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
            thread = {"posts": []}
            current_section = "thread"
            continue
        elif line.startswith("--- End Message Thread ---"):
            data["threads"].append(thread)
            thread = {}
            current_section = None
            continue
        elif line.startswith("--- Start Message Post ---"):
            message = {}
            current_section = "message"
            continue
        elif line.startswith("--- End Message Post ---"):
            thread["posts"].append(message)
            message = {}
            current_section = "thread"
            continue
        elif line.startswith("--- Start Message Body ---"):
            current_section = "message_body"
            message["body"] = ""
            continue
        elif line.startswith("--- End Message Body ---"):
            current_section = "message"
            continue

        if current_section == "info":
            data["info"] += line + "\n"
        elif current_section == "user":
            if ":" in line:
                k, v = line.split(":", 1)
                user[k.strip()] = v.strip()
        elif current_section == "user_bio":
            user["bio"] += line + "\n"
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
            message["body"] += line + "\n"

    return data

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
    parser = argparse.ArgumentParser(description="Parse message board archive TXT to JSON/YAML.")
    parser.add_argument("input", help="Path to input .txt file")
    parser.add_argument("--json", help="Output JSON file", default="archive.json")
    parser.add_argument("--yaml", help="Output YAML file", default="archive.yaml")
    parser.add_argument("--print", action="store_true", help="Print parsed output to terminal")

    args = parser.parse_args()

    parsed = parse_txt_archive(args.input)

    if args.print:
        print(json.dumps(parsed, indent=2))

    save_json(parsed, args.json)

    if HAS_YAML:
        save_yaml(parsed, args.yaml)

if __name__ == "__main__":
    main()
