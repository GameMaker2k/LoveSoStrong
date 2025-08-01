#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import pytextarchive.parse_message_file
import pytextarchive.archive_parser
import pytextarchive.mini_parser

__program_name__ = "PyTextArchive"
__project__ = __program_name__
__project_url__ = "https://github.com/GameMaker2k/PyTextArchive"
__version_info__ = (0, 4, 10, "RC 1", 1)
__version_date_info__ = (2025, 7, 26, "RC 1", 1)
__version_date__ = str(__version_date_info__[0]) + "." + str(__version_date_info__[1]).zfill(2) + "." + str(__version_date_info__[2]).zfill(2)
__revision__ = __version_info__[3]
__revision_id__ = "$Id$"
if(__version_info__[4] is not None):
 __version_date_plusrc__ = __version_date__ + "-" + str(__version_date_info__[4])
if(__version_info__[4] is None):
 __version_date_plusrc__ = __version_date__
if(__version_info__[3] is not None):
 __version__ = str(__version_info__[0]) + "." + str(__version_info__[1]) + "." + str(__version_info__[2]) + " " + str(__version_info__[3])
if(__version_info__[3] is None):
 __version__ = str(__version_info__[0]) + "." + str(__version_info__[1]) + "." + str(__version_info__[2])

def init_empty_service(entry, service_name, service_type, service_location, time_zone="UTC", info=''):
    """ Initialize an empty service structure """
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

def add_user(service, user_id, name, handle, emailaddr, phonenum, location, website, avatar, banner, joined, birthday, hashtags, pinnedmessage, extrafields, bio, signature):
    """ Add a user to the service """
    service['Users'][user_id] = {
        'Name': name,
        'Handle': handle,
        'Email': emailaddr,
        'Phone': phonenum,
        'Location': location,
        'Website': website,
        'Avatar': website,
        'Banner': website,
        'Joined': joined,
        'Birthday': birthday,
        'HashTags': hashtags,
        'PinnedMessage': pinnedmessage,
        'ExtraFields': extrafields,
        'Bio': bio,
        'Signature': signature
    }

def add_category(service, kind, category_type, category_level, category_id, insub, headline, description):
    category = {
        'Kind': "{0}, {1}".format(kind, category_level),
        'Type': category_type,
        'Level': category_level,
        'ID': category_id,
        'InSub': insub,
        'Headline': headline,
        'Description': description
    }
    service['Categories'].append(category)
    if category_type not in service['Categorization']:
        service['Categorization'][category_type] = []
    if category_level not in service['Categorization'][category_type]:
        service['Categorization'][category_type].append(category_level)
    if insub != 0:
        if not any(cat['ID'] == insub for cat in service['Categories']):
            raise ValueError("InSub value '{0}' does not match any existing ID in service.".format(insub))

def add_message_thread(service, thread_id, title, category, forum, thread_type, thread_state, thread_keywords):
    """ Add a message thread to the service """
    thread = {
        'Thread': thread_id,
        'Title': title,
        'Category': category.split(',') if category else [],
        'Forum': forum.split(',') if forum else [],
        'Type': thread_type,
        'State': thread_state,
        'Keywords': thread_keywords,
        'Messages': []
    }
    service['MessageThreads'].append(thread)

def add_message_post(service, thread_id, author, authorid, time, date, edittime, editdate, editauthor, editauthorid, subtype, tags, post_id, pinned_id, nested, message):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread is not None:
        new_post = {
            'Author': author,
            'AuthorID': authorid,
            'Time': time,
            'Date': date,
            'EditTime': edittime,
            'EditDate': editdate,
            'EditAuthor': editauthor,
            'EditAuthorID': editauthorid,
            'SubType': subtype,
            'SubTitle': subtitle,
            'Tags': tags,
            'Post': post_id,
            'PinnedID': pinned_id,
            'Nested': nested,
            'Message': message
        }
        thread['Messages'].append(new_post)
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def add_poll(service, thread_id, post_id, poll_num, question, answers, results, percentages, votes):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread is not None:
        message = next((m for m in thread['Messages'] if m['Post'] == post_id), None)
        if message is not None:
            if 'Polls' not in message:
                message['Polls'] = []
            new_poll = {
                'Num': poll_num,
                'Question': question,
                'Answers': answers,
                'Results': results,
                'Percentage': percentages,
                'Votes': votes
            }
            message['Polls'].append(new_poll)
        else:
            raise ValueError("Post ID {0} not found in thread {1}.".format(post_id, thread_id))
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def remove_user(service, user_id):
    if user_id in service['Users']:
        del service['Users'][user_id]
    else:
        raise ValueError("User ID {0} not found in service.".format(user_id))

def remove_category(service, category_id):
    category = next((c for c in service['Categories'] if c['ID'] == category_id), None)
    if category:
        service['Categories'].remove(category)
    else:
        raise ValueError("Category ID {0} not found in service.".format(category_id))

def remove_message_thread(service, thread_id):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread:
        service['MessageThreads'].remove(thread)
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def remove_message_post(service, thread_id, post_id):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread is not None:
        message = next((m for m in thread['Messages'] if m['Post'] == post_id), None)
        if message is not None:
            thread['Messages'].remove(message)
        else:
            raise ValueError("Post ID {0} not found in thread {1}.".format(post_id, thread_id))
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def add_service(services, entry, service_name, service_type, service_location, time_zone="UTC", info=None):
    new_service = {
        'Entry': entry,
        'Service': service_name,
        'ServiceType': service_type,
        'ServiceLocation': service_location,
        'TimeZone': time_zone,
        'Info': info if info else '',
        'Interactions': [],
        'Status': [],
        'Categorization': {'Categories': [], 'Forums': []},
        'Categories': [],
        'Users': {},
        'MessageThreads': []
    }
    services.append(new_service)
    return new_service  # Return the newly created service

def remove_service(services, entry):
    service = next((s for s in services if s['Entry'] == entry), None)
    if service:
        services.remove(service)
    else:
        raise ValueError("Service entry {0} not found.".format(entry))
