# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import cherrypy
import sys

try:
    from parse_message_file import services_to_html_from_file, to_json_from_file, to_yaml_from_file
except ImportError:
    def services_to_html_from_file(filepath):
        with open(filepath, "r") as f:
            return "<pre>{}</pre>".format(f.read())
    def to_json_from_file(filepath):
        with open(filepath, "r") as f:
            return f.read()
    def to_yaml_from_file(filepath):
        with open(filepath, "r") as f:
            return f.read()

HTML_START = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Text Archives</title>
</head>
<body>
'''

HTML_END = '''
</body>
</html>'''

class ArchiveBrowser(object):
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir

    @cherrypy.expose
    def index(self):
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith(".txt")]
        except Exception as e:
            return HTML_START + "<h2>Error reading directory: {}</h2>\n".format(e) + HTML_END

        links = []
        for f in sorted(files):
            base = f[:-4] if f.endswith(".txt") else f
            html_link = '<a href="/{}.html">{}</a>'.format(base, f)
            txt_link = '<a href="/{}.txt">(source)</a>'.format(base)
            json_link = '<a href="/{}.json">json</a>'.format(base)
            links.append('  <li>{} {} {}</li>'.format(html_link, txt_link, json_link))

        content = "<h1>Text Archives</h1>\n<ul>\n" + "\n".join(links) + "\n</ul>"
        return HTML_START + content + HTML_END

    @cherrypy.expose
    def default(self, filename):
        safe_filename = os.path.basename(filename)
        base, ext = os.path.splitext(safe_filename)
        filepath = os.path.join(self.data_dir, base + ".txt")

        if not os.path.isfile(filepath):
            return HTML_START + "<h2>File not found</h2>\n" + HTML_END

        if ext == ".html":
            try:
                return services_to_html_from_file(filepath)
            except Exception as e:
                return HTML_START + "<h2>Error processing HTML: {}</h2>\n".format(e) + HTML_END

        elif ext == ".txt":
            try:
                with open(filepath, "r") as f:
                    raw = f.read()
                body = "<h2>Raw Source: {}</h2>\n<pre>{}</pre>".format(base + ".txt", raw)
                return HTML_START + body + HTML_END
            except Exception as e:
                return HTML_START + "<h2>Error reading file: {}</h2>\n".format(e) + HTML_END

        elif ext == ".json":
            try:
                cherrypy.response.headers['Content-Type'] = 'application/json'
                return to_json_from_file(filepath)
            except Exception as e:
                cherrypy.response.headers['Content-Type'] = 'text/html'
                return HTML_START + "<h2>Error generating JSON: {}</h2>\n".format(e) + HTML_END

        elif ext == ".yaml":
            try:
                cherrypy.response.headers['Content-Type'] = 'application/yaml'
                return to_yaml_from_file(filepath)
            except Exception as e:
                cherrypy.response.headers['Content-Type'] = 'text/html'
                return HTML_START + "<h2>Error generating YAML: {}</h2>\n".format(e) + HTML_END

        else:
            return HTML_START + "<h2>Unsupported file type</h2>\n" + HTML_END

config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080
    }
}

if __name__ == "__main__":
    cherrypy.quickstart(ArchiveBrowser(), '/', config)
