#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import argparse
import sys
from parse_message_file import (
    parse_file, display_services, to_json, from_json, load_from_json_file, save_to_json_file,
    services_to_string, save_services_to_file, services_to_html, save_services_to_html_file,
    to_yaml, from_yaml, load_from_yaml_file, save_to_yaml_file
)

def main():
    parser = argparse.ArgumentParser(description="Parse and display message file content.")
    parser.add_argument("filename", help="Path to the file to be parsed")
    parser.add_argument("--validate-only", "-v", action="store_true", help="Only validate the file without displaying")
    parser.add_argument("--verbose", "-V", action="store_true", help="Enable verbose mode")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--to-json", "-j", help="Convert the parsed data to JSON and save to a file")
    parser.add_argument("--from-json", "-J", help="Load the services data structure from a JSON file")
    parser.add_argument("--json-string", "-s", type=str, help="JSON string to parse if --from-json is specified")
    parser.add_argument("--to-yaml", "-y", help="Convert the parsed data to YAML and save to a file")
    parser.add_argument("--from-yaml", "-Y", help="Load the services data structure from a YAML file")
    parser.add_argument("--yaml-string", "-S", type=str, help="YAML string to parse if --from-json is specified")
    parser.add_argument("--to-html", "-H", help="Convert the parsed data to HTML and save to a file")
    parser.add_argument("--to-original", "-o", help="Convert the parsed data back to the original format and save to a file")
    parser.add_argument("--line-ending", "-l", choices=["lf", "cr", "crlf"], default="lf", help="Specify the line ending format for the output file")
    args = parser.parse_args()

    try:
        if args.from_json:
            if args.json_string:
                services = from_json(args.json_string)
            else:
                services = load_from_json_file(args.from_json)
            display_services(services)
        else:
            if args.validate_only:
                is_valid, error_message, error_line = parse_file(args.filename, validate_only=True, verbose=args.verbose)
                if is_valid:
                    print("The file '{0}' is valid.".format(args.filename))
                else:
                    print("Validation Error: {0}".format(error_message))
                    print("Line: {0}".format(error_line.strip()))
            else:
                services = parse_file(args.filename, verbose=args.verbose)
                if args.debug:
                    import pdb; pdb.set_trace()
                if args.to_json:
                    save_to_json_file(services, args.to_json)
                    print("Saved JSON to {0}".format(args.to_json))
                elif args.to_yaml:
                    save_to_yaml_file(services, args.to_yaml)
                    print("Saved YAML to {0}".format(args.to_yaml))
                elif args.to_html:
                    save_services_to_html_file(services, args.to_html)
                    print("Saved HTML to {0}".format(args.to_html))
                elif args.to_original:
                    save_services_to_file(services, args.to_original, line_ending=args.line_ending)
                    print("Saved original format to {0}".format(args.to_original))
                else:
                    display_services(services)
    except Exception as e:
        print("An error occurred: {0}".format(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
