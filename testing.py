import re
import io
import os

ARCHIVE_FILE = "./data/archive_xtwitter_lf.txt"
HTML_OUTPUT_FILE = "./services_report.html"

def read_file(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)

def extract_block(start, end, text):
    pattern = r"{0}(.*?){1}".format(re.escape(start), re.escape(end))
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_users(section):
    user_blocks = re.findall(r"--- Start User Info ---.*?--- End User Info ---", section, re.DOTALL)
    users = []
    for block in user_blocks:
        name = re.search(r"Name: (.*?)\n", block)
        handle = re.search(r"Handle: (.*?)\n", block)
        bio = extract_block("--- Start Bio Body ---", "--- End Bio Body ---", block)
        users.append((name.group(1) if name else "", handle.group(1) if handle else "", bio))
    return users

def extract_threads(section):
    thread_blocks = re.findall(r"--- Start Message Thread ---.*?--- End Message Thread ---", section, re.DOTALL)
    threads = []
    for thread in thread_blocks:
        title_match = re.search(r"Title: (.*?)\n", thread)
        title = title_match.group(1).strip() if title_match else "Untitled Thread"
        posts = re.findall(
            r"--- Start Message Post ---.*?Author: (.*?)\nTime: (.*?)\nDate: (.*?)\n.*?Message:\n--- Start Message Body ---\n(.*?)\n--- End Message Body ---",
            thread,
            re.DOTALL
        )
        threads.append((title, posts))
    return threads

html = u"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Services Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }}
    .service-card {{ background: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 16px; margin-bottom: 40px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .thread-card {{ background: #fefefe; border-left: 4px solid #007BFF; padding: 12px; margin: 10px 0; }}
    .message-list {{ list-style: none; padding-left: 0; }}
    .message-list li {{ margin-bottom: 16px; }}
    blockquote {{ white-space: pre-wrap; border-left: 3px solid #ccc; padding-left: 10px; color: #444; }}
    .timestamp {{ font-size: 0.9em; color: #666; margin-bottom: 5px; }}
  </style>
</head>
<body>
<div class="service-card">
"""

# Read and parse
content = read_file(ARCHIVE_FILE)
services = re.findall(r"--- Start Archive Service ---(.*?)--- End Archive Service ---", content, re.DOTALL)

for idx, service in enumerate(services, 1):
    service_name = re.search(r"Service: (.*?)\n", service)
    title = service_name.group(1) if service_name else "Untitled Service"
    info = extract_block("--- Start Info Body ---", "--- End Info Body ---", service)
    html += u"<h2>Service Entry: {0} — {1}</h2>\n".format(idx, title)
    html += u"<p><strong>Info:</strong> <blockquote>{0}</blockquote></p>\n".format(info)

    # Users
    html += u"<h3>Users</h3><ul>\n"
    for uid, (name, handle, bio) in enumerate(extract_users(service), 1):
        html += u"<li><strong>{0}</strong>: {1} ({2})</li>\n<blockquote>{3}</blockquote>\n".format(uid, name, handle, bio)
    html += u"</ul>\n"

    # Threads
    html += u"<h3>Message Threads</h3>\n"
    for title, posts in extract_threads(service):
        html += u'<div class="thread-card">\n<h4>{0}</h4>\n<ul class="message-list">'.format(title)
        for author, time, date, msg in posts:
            html += u'<li><p class="timestamp">{0} — {1}</p><strong>{2}</strong>:<blockquote>{3}</blockquote></li>\n'.format(date, time, author, msg)
        html += u"</ul></div>\n"

    html += u"<hr/>\n"

html += u"</div></body></html>"

write_file(HTML_OUTPUT_FILE, html)
print("✅ HTML report generated: {}".format(HTML_OUTPUT_FILE))
