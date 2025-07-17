#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import argparse
import json
import re
import os
import sys
import io
import gzip

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

def parse_txt_archive(filepath):
    data = {
        "info": "",
        "users": [],
        "categories": [],
        "forums": [],
        "threads": [],
        "polls": [],
        "includes": []
    }

    with open_text_file(filepath) as f:
        lines = f.readlines()

    current_section = None
    user = {}
    category = {}
    thread = {}
    message = {}
    poll = {}

    for line in lines:
        line = line.strip()

        if line.startswith("--- Include Service Start ---"):
            current_section = "include"
            continue
        elif line.startswith("--- Include Service End ---"):
            current_section = None
            continue
        elif current_section == "include":
            data["includes"].append(line)
            continue

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
        elif line.startswith("--- Start Poll Body ---"):
            poll = {}
            current_section = "poll"
            continue
        elif line.startswith("--- End Poll Body ---"):
            data["polls"].append(poll)
            poll = {}
            current_section = None
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
        elif current_section == "poll":
            if ":" in line:
                k, v = line.split(":", 1)
                poll[k.strip()] = v.strip()

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
    parser = argparse.ArgumentParser(description="Parse message board archive TXT with includes and polls.")
    parser.add_argument("input", help="Input .txt or .gz file")
    parser.add_argument("--json", default="out.json", help="Output JSON file")
    parser.add_argument("--yaml", default="out.yaml", help="Output YAML file")
    parser.add_argument("--print", action="store_true", help="Print parsed output")
    args = parser.parse_args()

    data = parse_txt_archive(args.input)

    if args.print:
        print(json.dumps(data, indent=2))

    save_json(data, args.json)
    if HAS_YAML:
        save_yaml(data, args.yaml)

if __name__ == "__main__":
    main()
