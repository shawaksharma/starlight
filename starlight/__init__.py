#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import json
import requests
from tabulate import tabulate
from HTMLParser import HTMLParser

log = []
h = HTMLParser()


class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_newlines(text):
    text = text.replace('<br>', ' ')
    text = text.replace('<br />', ' ')
    text = text.replace('<br/>', ' ')
    text = text.replace('\n', ' ')
    return text


def strip_html(text):
    if text == None:
        return str(text)
    text = h.unescape(strip_newlines(text))
    s = MLStripper()
    s.feed(text)
    return s.get_data().strip()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_response(request):
    try:
        req = requests.get('https://data.police.uk/api/%s' % request)
        data = json.loads(req.text.encode('utf8'))
    except ValueError:
        return 1, '\nSomething went wrong! Server responded with status code %d. Remember options are case sensitive.' % req.status_code
    except requests.exceptions.ConnectionError:
        return 2, '\nSomething went wrong! Check your internet connection.'
    return 0, data


def get_options(required, logging=True):
    got_options = []
    print
    for option in required:
        i = raw_input('%s: ' % option).strip()
        got_options.append(i)
    confirm = raw_input('Are those options correct? ').strip().lower()
    if confirm == 'y' or confirm == 'yes':
        if logging == True:
            index = 0
            for option in got_options:
                logit('%s: %s\n' % (required[index], option))
                index += 1
            logit('\n')
        return got_options
    else:
        return get_options(required)


def grab(element, field, struct='{s}'):
    try:
        data = element[field]
        if not data or data == None:
            return ''
    except:
        return ''
    if isinstance(data, basestring):
        return struct.replace('{s}', strip_html(data))
    return True


def logit(line):
    global log
    log.append(line)


def crime_last_updated():
    err, resp = get_response('crime-last-updated')
    if not err:
        return validate('Crime data was last updated on: %s\n' % resp['date'])
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def crime_categories():
    output = [['Name', 'ID']]
    err, resp = get_response('crime-categories')
    if not err:
        for entity in resp:
            output.append([entity['name'],
                           entity['url']])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def locate(options):
    output = [['Force', 'Neighbourhood']]
    err, resp = get_response('locate-neighbourhood?q=%s,%s' % (options[0], options[1]))
    if not err:
        output.append([resp['force'],
                       resp['neighbourhood']])
        return validate(output)
    elif err == 1:
        logit('Invalid coordinates.\n\n')
        return 'Invalid coordinates.'
    else:
        logit('Connection error.\n\n')
        return resp


def forces():
    output = [['Name', 'ID']]
    err, resp = get_response('forces')
    if not err:
        for entity in resp:
            output.append([entity['name'],
                           entity['id']])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def force_info(options):
    output = ''
    err, resp = get_response('forces/%s' % options[0])
    if not err:
        output += '%s\nPhone Number: %s\nURL: %s\n' % (resp['name'],
                                                       resp['telephone'],
                                                       resp['url'])
        if len(resp['engagement_methods']):
            output += 'Engagement Info:\n'
            for entity in resp['engagement_methods']:
                output += '  %s: %s\n' % (entity['title'],
                                          entity['url'])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def force_officers(options):
    output = ''
    err, resp = get_response('forces/%s/people' % options[0])
    if not err:
        for officer in resp:
            output += 'Name: %s\nRank: %s\n' % (officer['name'],
                                                officer['rank'])
            if len(officer['contact_details']):
                output += 'Contact Details:\n'
                for entry in officer['contact_details']:
                    output += '  %s: %s\n' % (entry.title(),
                                              officer['contact_details'][entry])
            output += 'Biography:\n  %s\n\n' % strip_html(officer['bio'])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def neighbourhoods(options):
    output = [['Name', 'ID']]
    err, resp = get_response('%s/neighbourhoods' % options[0])
    if not err:
        for entity in resp:
            output.append([entity['name'],
                           entity['id']])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def neighbourhood_info(options):
    output = ''
    err, resp = get_response('%s/%s' % (options[0], options[1]))
    if not err:
        output += '%s (%s) (Population: %s)\n\n' % (resp['name'],
                                                    resp['id'],
                                                    resp['population'])
        output += grab(resp, 'welcome_message', 'Welcome message: {s}\n\n')
        output += grab(resp, 'description', 'Description:\n  {s}\n\n')
        output += grab(resp['centre'], 'latitude', 'Coordinates of centre: {s} N,')
        output += grab(resp['centre'], 'longitude', ' {s} W\n\n')
        output += '%s%s\n' % (grab(resp, 'url_force', 'Force URL: {s}\n'),
                              grab(resp, 'url_boundary', 'Boundary URL: {s}\n'))
        if grab(resp, 'links'):
            output += 'Links:\n'
            for link in resp['links']:
                output += '  %s: %s\n' % (strip_html(link['title']),
                                          link['url'])
                output += grab(link, 'description', '    Description: {s}\n')
            output += '\n'
        if grab(resp, 'locations'):
            output += 'Significant locations:\n'
            for location in resp['locations']:
                output += '  %s %s\n' % (grab(location, 'name'),
                                         grab(location, 'type', '({s})'))
                output += '    Address: %s\n    Postcode: %s\n' % (grab(location, 'address'),
                                                                   grab(location, 'postcode'))
                output += grab(location, 'latitude', '    Coordinates: {s} N,')
                output += grab(location, 'longitude', ' {s} W\n')
                output += grab(location, 'telephone', '    Telephone number: {s}\n')
                output += grab(location, 'description', '    Description:\n        {s}\n')
                output += '\n'
        if len(resp['contact_details']):
            output += 'Contact Details:\n'
            for entry in resp['contact_details']:
                output += '  %s: %s\n' % (entry.title(),
                                          resp['contact_details'][entry])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def neighbourhood_boundary(options):
    output = [['Latitude', 'Longitude']]
    err, resp = get_response('%s/%s/boundary' % (options[0], options[1]))
    if not err:
        for pair in resp:
            output.append([pair['latitude'], pair['longitude']])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def neighbourhood_officers(options):
    output = ''
    err, resp = get_response('%s/%s/people' % (options[0], options[1]))
    if not err:
        for officer in resp:
            output += 'Name: %s\nRank: %s\n' % (officer['name'],
                                                officer['rank'])
            if len(officer['contact_details']):
                output += 'Contact Details:\n'
                for entry in officer['contact_details']:
                    output += '  %s: %s\n' % (entry.title(),
                                              officer['contact_details'][entry])
            output += 'Biography:\n  %s\n\n' % strip_html(officer['bio'])
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def neighbourhood_issues(options):
    output = ''
    err, resp = get_response('%s/%s/priorities' % (options[0], options[1]))
    if not err:
        for issue in resp:
            output += grab(issue, 'issue-date', 'Issue date: {s}\n')
            output += grab(issue, 'issue', 'Issue:\n  {s}\n')
            output += grab(issue, 'action-date', 'Action date: {s}\n')
            output += grab(issue, 'action', 'Action:\n  {s}\n')
            output += '\n'
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def neighbourhood_events(options):
    output = ''
    err, resp = get_response('%s/%s/events' % (options[0], options[1]))
    if not err:
        for event in resp:
            output += grab(event, 'title')
            output += grab(event, 'type', ' - ({s})\n')
            output += grab(event, 'start_date', 'Date: {s}\n')
            output += grab(event, 'address', 'Address: {s}\n')
            output += grab(event, 'description', 'Description:\n  {s}\n')
            if len(event['contact_details']):
                output += 'Contact Details:\n'
                for entry in event['contact_details']:
                    output += '  %s: %s\n' % (entry.title(),
                                              event['contact_details'][entry])
            output += '\n'
        return validate(output)
    else:
        logit('Server error.\n\n' if err == 1 else 'Connection error.\n\n')
        return resp


def save():
    global log
    if log:
        file_name = get_options(['File Name'], False)[0]
        print '\nAppending logs to %s...' % file_name
        try:
            with open(file_name, 'a') as f:
                for entry in log:
                    f.write(entry.encode('utf8'))
            log = []
            print 'Successfully saved data to %s.' % file_name
            print 'Cleared logs from memory.'
        except IOError:
            print 'Couldn\'t open that file for writing!'
    else:
        print '\nThere\'s no logs to save!'


def validate(response):
    if response:
        if isinstance(response, basestring):
            logit('%s\n' % response)
            return '\n%s' % response.strip()
        else:
            formatted = tabulate(response, headers='firstrow', tablefmt='fancy_grid')
            logit('%s\n\n' % formatted)
            return '\n%s' % formatted
    else:
        logit('No data available.\n\n')
        return '\nNo data available.'


def interactive():
    print """
                   _____ __             ___       __    __
                  / ___// /_____ ______/ (_)___ _/ /_  / /_
                  \__ \/ __/ __ `/ ___/ / / __ `/ __ \/ __/
                 ___/ / /_/ /_/ / /  / / / /_/ / / / / /_
                /____/\__/\__,_/_/  /_/_/\__, /_/ /_/\__/
                                        /____/

    A simplified command-line interface for the official UK police API.

    Please report any issues at https://github.com/libeclipse/starlight/issues

    Use `help` for a list of commands."""
    saveable = [
        'last-updated',
        'categories',
        'locate',
        'list',
        'officers',
        'info',
        'boundary',
        'issues',
        'events'
    ]
    while True:
        command = raw_input('\n/ >> ').strip().lower()
        if command in saveable:
            logit('/ >> %s\n\n' % command)
        if command == 'help' or command == 'ls':
            print """
  `help`                -   Prints this help message.
  `crimes`              -   Crime related stuff.
  `forces`              -   Force related stuff.
  `neighbourhoods`      -   Neighbourhood related stuff.
  `save`                -   Saves the whole session's logs to file.
  `clear`               -   Clears the terminal window.
  `exit`                -   Exits the program."""
        elif 'crime' in command:
            while True:
                command = raw_input('\n/crimes/ >> ').strip().lower()
                if command in saveable:
                    logit('/crimes/ >> %s\n\n' % command)
                if command == 'help' or command == 'ls':
                    print """
  `help`            -   Prints this help message.
  `last-updated`    -   Returns the date the crime data was last updated.
  `categories`      -   Lists all the crime categories and their IDs.
  `save`            -   Saves the whole session's log to file.
  `clear`           -   Clears the terminal window.
  `back`            -   Back to main menu.
  `exit`            -   Exits the program."""
                elif command == 'last-updated':
                    print crime_last_updated()
                elif command == 'categories':
                    print crime_categories()
                elif command == 'save':
                    save()
                elif command == 'clear':
                    clear()
                elif command == 'back' or '..' in command:
                    break
                elif command == 'exit':
                    print '\nExiting...'
                    raise SystemExit
                else:
                    print '\nUnknown command. Use `help` for help.'
        elif 'force' in command:
            while True:
                command = raw_input('\n/forces/ >> ').strip().lower()
                if command in saveable:
                    logit('/forces/ >> %s\n\n' % command)
                if command == 'help' or command == 'ls':
                    print """
  `help`        -   Prints this help message.
  `list`        -   Lists all forces and their IDs.
  `info`        -   Returns information about a specific force.
  `officers`    -   Returns information about the senior officer[s] of a given force.
  `save`        -   Saves the whole session's log to file.
  `clear`       -   Clears the terminal window.
  `back`        -   Back to main menu.
  `exit`        -   Exits the program."""
                elif command == 'list':
                    print forces()
                elif command == 'info':
                    options = get_options(['Force ID'])
                    print force_info(options)
                elif command == 'officers':
                    options = get_options(['Force ID'])
                    print force_officers(options)
                elif command == 'save':
                    save()
                elif command == 'clear':
                    clear()
                elif command == 'back' or '..' in command:
                    break
                elif command == 'exit':
                    print '\nExiting...'
                    raise SystemExit
                else:
                    print '\nUnknown command. Use `help` for help.'
        elif 'neighbourhood' in command:
            while True:
                command = raw_input('\n/neighbourhoods/ >> ').strip().lower()
                if command in saveable:
                    logit('/neighbourhoods/ >> %s\n\n' % command)
                if command == 'help' or command == 'ls':
                    print """
  `help`        -   Prints this help message.
  `list`        -   Lists all forces and their IDs.
  `info`        -   Returns information about a specific force.
  `locate`      -   Returns the force and neighbourhood for a given coordinate.
  `boundary`    -   Lists the boundary coordinates of a neighbourhood.
  `officers`    -   Returns information about the officer[s] of a given neighbourhood.
  `issues`      -   Returns the neighbourhood police force's priorities.
  `events`      -   Returns a list of scheduled neighbourhood events.
  `save`        -   Saves the whole session's log to file.
  `clear`       -   Clears the terminal window.
  `back`        -   Back to main menu.
  `exit`        -   Exits the program."""
                elif command == 'list':
                    options = get_options(['Force ID'])
                    print neighbourhoods(options)
                elif command == 'info':
                    options = get_options(['Force ID', 'Neighbourhood ID'])
                    print neighbourhood_info(options)
                elif command == 'locate':
                    options = get_options(['Latitude', 'Longitude'])
                    print locate(options)
                elif command == 'boundary':
                    options = get_options(['Force ID', 'Neighbourhood ID'])
                    print neighbourhood_boundary(options)
                elif command == 'officers':
                    options = get_options(['Force ID', 'Neighbourhood ID'])
                    print neighbourhood_officers(options)
                elif command == 'issues':
                    options = get_options(['Force ID', 'Neighbourhood ID'])
                    print neighbourhood_issues(options)
                elif command == 'events':
                    options = get_options(['Force ID', 'Neighbourhood ID'])
                    print neighbourhood_events(options)
                elif command == 'save':
                    save()
                elif command == 'clear':
                    clear()
                elif command == 'back' or '..' in command:
                    break
                elif command == 'exit':
                    print '\nExiting...'
                    raise SystemExit
                else:
                    print '\nUnknown command. Use `help` for help.'
        elif command == 'save':
            save()
        elif command == 'clear':
            clear()
        elif command == 'back' or '..' in command:
            pass
        elif command == 'exit':
            print '\nExiting...'
            break
        else:
            print '\nUnknown command. Use `help` for help.'

def main():
    try:
        interactive()
    except KeyboardInterrupt:
        print '\nKeyboard Interrupt.'
    except Exception, e:
        print '\nFATAL ERROR: %s\n' % e
        print 'Please report this error at https://github.com/libeclipse/starlight/issues'

if __name__ == "__main__":
    main()
