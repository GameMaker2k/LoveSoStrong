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

def init_empty_service(entry, service_name, service_type, service_location, time_zone="UTC", info=''):
    return {
        'Entry': entry,
        'Service': service_name,
        'ServiceType': service_type,
        'ServiceLocation': service_location,
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
    service = init_empty_service("default-entry", "MessageBoard", "MessageBoard", "", "UTC", "")

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
    parser.add_argument("--export-txt", help="Export full archive format file")
    parser.add_argument("--write-txt", help="Recreate original-style .txt output")
    args = parser.parse_args()
    if args.export_txt:
        write_services_to_txt_file([service], args.export_txt)

    if args.write_txt:
        write_service_to_txt(service, args.write_txt)


    service = parse_txt_archive(args.input)

    if args.print:
        print(json.dumps(service, indent=2))

    save_json(service, args.json)
    if HAS_YAML:
        save_yaml(service, args.yaml)



def write_service_to_txt(service, out_path):
    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write("--- Start Info Body ---\n")
        f.write(service.get("Info", "").strip() + "\n")
        f.write("--- End Info Body ---\n\n")

        for uid, user in service.get("Users", {}).items():
            f.write("--- Start User Info ---\n")
            for k, v in user.items():
                if k != "Bio":
                    f.write("{0}: {1}\n".format(k, v))
            f.write("--- Start Bio Body ---\n")
            f.write(user.get("Bio", "").strip() + "\n")
            f.write("--- End Bio Body ---\n")
            f.write("--- End User Info ---\n\n")

        for cat in service.get("Categories", []):
            f.write("--- Start Category List ---\n")
            for k, v in cat.items():
                if k != "Description":
                    f.write("{0}: {1}\n".format(k, v))
            f.write("--- Start Description Body ---\n")
            f.write(cat.get("Description", "").strip() + "\n")
            f.write("--- End Description Body ---\n")
            f.write("--- End Category List ---\n\n")

        for thread in service.get("MessageThreads", []):
            f.write("--- Start Message Thread ---\n")
            for k, v in thread.items():
                if k != "Messages":
                    f.write("{0}: {1}\n".format(k, v))
            for post in thread.get("Messages", []):
                f.write("--- Start Message Post ---\n")
                for k, v in post.items():
                    if k == "Message":
                        continue
                    f.write("{0}: {1}\n".format(k, v))
                f.write("--- Start Message Body ---\n")
                f.write(post.get("Message", "").strip() + "\n")
                f.write("--- End Message Body ---\n")
                f.write("--- End Message Post ---\n")
            f.write("--- End Message Thread ---\n\n")

    print("[✔] Service structure written back to {}".format(out_path))

def services_to_string(services, line_ending='lf'):
    output = []

    for service in services:
        output.append('--- Start Archive Service ---')
        output.append('Entry: {0}'.format(service.get('Entry', '')))
        output.append('Service: {0}'.format(service.get('Service', '')))
        output.append('ServiceType: {0}'.format(service.get('ServiceType', '')))
        output.append('ServiceLocation: {0}'.format(service.get('ServiceLocation', '')))
        output.append('TimeZone: {0}'.format(service.get('TimeZone', 'UTC')))

        if 'Info' in service:
            output.append('Info:')
            output.append('--- Start Info Body ---')
            output.extend(service['Info'].splitlines())
            output.append('--- End Info Body ---')
            output.append('')

        users = service.get('Users', {})
        if users:
            output.append('--- Start User List ---')
            for uid, user in users.items():
                output.append('--- Start User Info ---')
                output.append('User: {0}'.format(uid))
                output.append('Name: {0}'.format(user.get('Name', '')))
                output.append('Handle: {0}'.format(user.get('Handle', '')))
                output.append('Email: {0}'.format(user.get('Email', '')))
                output.append('Phone: {0}'.format(user.get('Phone', '')))
                output.append('Location: {0}'.format(user.get('Location', '')))
                output.append('Website: {0}'.format(user.get('Website', '')))
                output.append('Avatar: {0}'.format(user.get('Avatar', '')))
                output.append('Banner: {0}'.format(user.get('Banner', '')))
                output.append('Joined: {0}'.format(user.get('Joined', '')))
                output.append('Birthday: {0}'.format(user.get('Birthday', '')))
                output.append('HashTags: {0}'.format(user.get('HashTags', '')))
                output.append('Bio:')
                output.append('--- Start Bio Body ---')
                output.extend(user.get('Bio', '').splitlines())
                output.append('--- End Bio Body ---')
                output.append('--- End User Info ---')
                output.append('')
            output.append('--- End User List ---')
            output.append('')

        if service.get('Categorization'):
            cat = service['Categorization']
            output.append('--- Start Categorization List ---')
            output.append('Categories: {0}'.format(', '.join(cat.get('Categories', []))))
            output.append('Forums: {0}'.format(', '.join(cat.get('Forums', []))))
            output.append('--- End Categorization List ---')
            output.append('')

        for cat in service.get('Categories', []):
            output.append('--- Start Category List ---')
            output.append('Kind: {0}, {1}'.format(cat.get('Type', ''), cat.get('Level', '')))
            output.append('ID: {0}'.format(cat.get('ID', '')))
            output.append('InSub: {0}'.format(cat.get('InSub', '')))
            output.append('Headline: {0}'.format(cat.get('Headline', '')))
            output.append('Description:')
            output.append('--- Start Description Body ---')
            output.extend(cat.get('Description', '').splitlines())
            output.append('--- End Description Body ---')
            output.append('--- End Category List ---')
            output.append('')

        threads = service.get('MessageThreads', [])
        if threads:
            output.append('--- Start Message List ---')
            if service.get('Interactions'):
                output.append('Interactions: {0}'.format(', '.join(service['Interactions'])))
            if service.get('Status'):
                output.append('Status: {0}'.format(', '.join(service['Status'])))
            output.append('')

            for thread in threads:
                output.append('--- Start Message Thread ---')
                output.append('Thread: {0}'.format(thread.get('Thread', '')))
                output.append('Title: {0}'.format(thread.get('Title', '')))
                output.append('Type: {0}'.format(thread.get('Type', '')))
                output.append('State: {0}'.format(thread.get('State', '')))
                output.append('Keywords: {0}'.format(thread.get('Keywords', '')))
                output.append('Category: {0}'.format(', '.join(thread.get('Category', []))))
                output.append('Forum: {0}'.format(', '.join(thread.get('Forum', []))))
                output.append('')

                for msg in thread.get('Messages', []):
                    output.append('--- Start Message Post ---')
                    output.append('Author: {0}'.format(msg.get('Author', '')))
                    output.append('Time: {0}'.format(msg.get('Time', '')))
                    output.append('Date: {0}'.format(msg.get('Date', '')))
                    output.append('SubType: {0}'.format(msg.get('SubType', '')))
                    if 'SubTitle' in msg:
                        output.append('SubTitle: {0}'.format(msg.get('SubTitle', '')))
                    if 'Tags' in msg:
                        output.append('Tags: {0}'.format(msg.get('Tags', '')))
                    output.append('Post: {0}'.format(msg.get('Post', '')))
                    output.append('Nested: {0}'.format(msg.get('Nested', '')))
                    output.append('Message:')
                    output.append('--- Start Message Body ---')
                    output.extend(msg.get('Message', '').splitlines())
                    output.append('--- End Message Body ---')

                    if 'Polls' in msg and msg['Polls']:
                        output.append('Polls:')
                        output.append('--- Start Poll List ---')
                        for poll in msg['Polls']:
                            output.append('--- Start Poll Body ---')
                            output.append('Num: {0}'.format(poll.get('Num', '')))
                            output.append('Question: {0}'.format(poll.get('Question', '')))
                            output.append('Answers: {0}'.format(', '.join(poll.get('Answers', []))))
                            output.append('Results: {0}'.format(', '.join(str(r) for r in poll.get('Results', []))))
                            output.append('Percentage: {0}'.format(', '.join('{:.1f}'.format(float(p)) for p in poll.get('Percentage', []))))
                            output.append('Votes: {0}'.format(poll.get('Votes', '')))
                            output.append('--- End Poll Body ---')
                        output.append('--- End Poll List ---')
                    output.append('--- End Message Post ---')
                    output.append('')
                output.append('--- End Message Thread ---')
                output.append('')
            output.append('--- End Message List ---')
            output.append('')
        output.append('--- End Archive Service ---')
        output.append('')

    text = '\n'.join(output)
    if line_ending.lower() == 'crlf':
        text = text.replace('\n', '\r\n')
    return text

def write_services_to_txt_file(services, out_path, line_ending='lf'):
    content = services_to_string(services, line_ending)
    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[✔] Wrote full archive file to {}".format(out_path))

if __name__ == "__main__":
    main()
