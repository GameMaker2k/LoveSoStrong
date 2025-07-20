#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import json

def encode_to_text_v2(data):
    from collections import defaultdict
    threads = defaultdict(list)
    for row in data:
        msg_id, author, message, thread, category, timestamp, nested = row
        threads[(thread.strip(), category.strip())].append({
            "id": msg_id,
            "author": author.strip(),
            "time": timestamp.strip(),
            "nested": nested,
            "message": message.strip()
        })

    lines = [
        "# Archive Info",
        "SERVICE: ChatGPT Interaction Log",
        "TYPE: Interactive Chat",
        "LOCATION: https://chatgpt.com/",
        "TIMEZONE: UTC",
        "INFO: ChatGPT is a chatbot developed by OpenAI.",
        "",
        "# Threads"
    ]

    for (thread, category), messages in threads.items():
        lines.append("THREAD: {} | Category: {}".format(thread, category))
        lines.append("")
        for msg in messages:
            lines.append("ID: {}".format(msg["id"]))
            lines.append("Author: {}".format(msg["author"]))
            lines.append("Time: {}".format(msg["time"]))
            lines.append("Nested: {}".format(msg["nested"]))
            lines.append("Message:")
            lines.extend(msg["message"].splitlines())
            lines.append("")  # blank line between messages

    return "\n".join(lines)


def decode_from_text_v2(text):
    lines = text.strip().splitlines()
    data = []
    thread = category = None
    msg = {}
    reading_message = False
    message_lines = []

    for line in lines:
        line = line.strip()
        if line.startswith("THREAD:"):
            if msg:
                msg["message"] = "\n".join(message_lines).strip()
                data.append([
                    msg["id"], msg["author"], msg["message"],
                    thread, category, msg["time"], int(msg["nested"])
                ])
                msg = {}
                message_lines = []
            parts = line[len("THREAD:"):].split("| Category:")
            thread = parts[0].strip()
            category = parts[1].strip() if len(parts) > 1 else "Uncategorized"
        elif line.startswith("ID:"):
            if msg and message_lines:
                msg["message"] = "\n".join(message_lines).strip()
                data.append([
                    msg["id"], msg["author"], msg["message"],
                    thread, category, msg["time"], int(msg["nested"])
                ])
                msg = {}
                message_lines = []
            msg["id"] = line[3:].strip()
        elif line.startswith("Author:"):
            msg["author"] = line[len("Author:"):].strip()
        elif line.startswith("Time:"):
            msg["time"] = line[len("Time:"):].strip()
        elif line.startswith("Nested:"):
            msg["nested"] = line[len("Nested:"):].strip()
        elif line.startswith("Message:"):
            message_lines = []
        elif line == "":
            continue
        else:
            message_lines.append(line)

    if msg and message_lines:
        msg["message"] = "\n".join(message_lines).strip()
        data.append([
            msg["id"], msg["author"], msg["message"],
            thread, category, msg["time"], int(msg["nested"])
        ])

    return data


def write_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)


def read_file(filename):
    with open(filename, "r") as f:
        return f.read()


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def usage():
    print("Usage:")
    print("  Encode JSON to archive format:")
    print("     python chat_archive_tool.py encode input.json output.txt")
    print("  Decode archive to JSON:")
    print("     python chat_archive_tool.py decode input.txt output.json")


def main():
    if len(sys.argv) != 4:
        usage()
        return

    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if command == "encode":
        data = load_json(input_file)
        result = encode_to_text_v2(data)
        write_file(output_file, result)
        print("✅ Encoded to:", output_file)
    elif command == "decode":
        text = read_file(input_file)
        result = decode_from_text_v2(text)
        save_json(output_file, result)
        print("✅ Decoded to:", output_file)
    else:
        usage()


if __name__ == "__main__":
    main()
