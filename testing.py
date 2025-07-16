from parse_message_file import *

services = []
s = add_service(services, entry=1, service_name="Test Board", time_zone="UTC", info="Script-generated board.")
add_user(s, 1, "Test User", "@testuser", "Web", "", "Today", "1990-01-01", "Testing things.")

add_category(s, "Categories", "Category", "Main", 1, 0, "General", "General talk.")
add_category(s, "Forums", "Forum", "Main", 1, 0, "Main Chat", "Main discussion area.")

add_message_thread(s, 1, "Welcome!", "General", "Main Chat", "Topic", "Pinned")
add_message_post(s, 1, "@testuser", "12:00 PM", "Today", "Post", "Welcome!", "", 1, 0, "Hello, this is a test.")

# Export
save_to_json_file(services, "output.json")
save_services_to_file(services, "output.txt")
save_services_to_html_file(services, "output.html")
