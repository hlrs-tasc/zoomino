#!/usr/bin/env python3

import argparse
import json
import jwt
import os
import pathlib
import sys
import zoomus


BASIC = 1
LICENSED = 2
user_types = {BASIC: "Basic", LICENSED: "Licensed"}

INSTANT = 1
SCHEDULED = 2
RECURRING_NO_FIXED_TIME = 3
RECURRING_FIXED_TIME = 8
meeting_types = {INSTANT: "Instant meeting", SCHEDULED: "Scheduled meeting",
                 RECURRING_NO_FIXED_TIME: "Recurring meeting with no fixed time",
                 RECURRING_FIXED_TIME: "Recurring meeting with fixed time"}


def main():
    # Verify JWT version
    if jwt.__version__.startswith("0.") or jwt.__version__.startswith("1."):
        version = jwt.__version__
        print(f"WARNING: package version for `jwt` must be 2.0.0 or greater (currently: {version})",
                file=sys.stderr)

    credentials = pathlib.Path(pathlib.Path.home(), ".zoomino_credentials.json")
    if not os.path.isfile(credentials):
        abort(f"no credentials file found at '{credentials}'")
    api = json.load(open(credentials))
    if "API_KEY" not in api:
        abort("'API_KEY' not found in credentials file")
    if "API_SECRET" not in api:
        abort("'API_SECRET' not found in credentials file")
    if "USER_EMAIL" not in api:
        abort("'USER_EMAIL' not found in credentials file")

    api_key = api["API_KEY"]
    api_secret = api["API_SECRET"]
    user_email = api["USER_EMAIL"]

    args = parse_arguments(user_email)

    with zoomus.ZoomClient(api_key, api_secret) as client:
        if args.command == "show":
            show_user(client, args.user)
        elif args.command == "list":
            show_all_users(client)
        elif args.command == "unassign":
            zoom_set_user_type(client, args.user, BASIC)
            show_user(client, args.user)
        elif args.command == "assign":
            users = zoom_get_all_users(client)
            target = args.user
            target_user = get_user(users, target)
            if target_user['type'] == LICENSED:
                show_user(client, target)
                return # Nothing to be done - we already have the license

            source = args.source
            if source == None:
                zoom_set_user_type(client, target, LICENSED)
                show_user(client, target)
                return

            source_user = get_user(users, source)
            if source_user['type'] != LICENSED:
                abort(f"user '{source}' does not have a license")

            zoom_set_user_type(client, source, BASIC)
            zoom_set_user_type(client, target, LICENSED)

            show_user(client, target)
        elif args.command == "list-meetings":
            show_all_meetings(client)


def parse_arguments(user_email):
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['show', 'assign', 'list', 'unassign', 'list-meetings'],
            help="Action to take",
            nargs='?',
            default="show")
    parser.add_argument('user', nargs='?', default=user_email,
            help="User to take action on (ignored for 'list' and 'list-meetings').")
    parser.add_argument('--from', '-f', dest="source",
            help="Required when multiple source users are available.")
    args = parser.parse_args()

    return args


def show_all_users(client):
    users = zoom_get_all_users(client)
    first = True
    for user in users:
        if first:
            first = False
        else:
            print()
        print_user(user)


def show_user(client, user_id):
    user = zoom_get_user(client, user_id)
    print_user(user)


def print_user(user):
    print("name:    ", user['first_name'], user['last_name'])
    print("email:   ", user['email'])
    print("type:    ", user_types[user['type']])


def zoom_get_all_users(client):
    response = client.user.list()
    if response.status_code != 200:
        abort(f"could not retrieve user list")

    user_list = json.loads(response.content)
    return user_list['users']


def zoom_get_all_meetings(client, meeting_type="upcoming", user_id="me"):
    response = client.meeting.list(user_id=user_id, type=meeting_type)
    if response.status_code != 200:
        abort(f"could not retrieve meetings list")

    meeting_list = json.loads(response.content)
    return meeting_list['meetings']


def print_meeting(meeting, user=None):
    if meeting["type"] == SCHEDULED or meeting["type"] == RECURRING_FIXED_TIME:
        start_time = meeting["start_time"]
        hours = int(meeting["duration"]) // 60
        minutes = int(meeting["duration"]) - 60*hours
        duration = "{:02d}:{:02d}h".format(hours, minutes)
    elif meeting["type"] == INSTANT:
        start_time = "Instant meeting"
        duration = "-"
    else:
        start_time = "Recurring meeting"
        duration = "-"

    print("topic:   ", meeting["topic"])
    print("start:   ", start_time)
    print("duration:", duration)
    if user:
        print("user:    ", user)
    print("url:     ", meeting["join_url"])


def show_all_meetings(client):
    users = zoom_get_all_users(client)
    first = True
    all_meetings = []
    for user in users:
        meetings = zoom_get_all_meetings(client, user_id=user['email'])
        for i, _ in enumerate(meetings):
            meetings[i]['user_first_name'] = user['first_name']
            meetings[i]['user_last_name'] = user['last_name']
            meetings[i]['user_email'] = user['email']
            meetings[i]['user_type'] = user_types[user['type']]
        all_meetings.extend(meetings)

    # The 'Z' ensures that all meetings without start time are listed last
    sorted_meetings = sorted(all_meetings, key=lambda x: (x.get('start_time', 'Z'), x['topic']))

    for meeting in sorted_meetings:
        if first:
            first = False
        else:
            print()
        print_meeting(meeting, user="{} {} ({}, {})".format(meeting['user_first_name'],
                meeting['user_last_name'], meeting['user_email'],
                meeting['user_type']))


def get_user(users, user_id):
    for user in users:
        if user['email'] == user_id or user['id'] == user_id:
            return user
    else:
        abort(f"user '{user_id}' not found")


def zoom_get_user(client, user_id):
    response = client.user.get(id=user_id)
    if response.status_code != 200:
        abort(f"could not retrieve user with id '{user_id}'")

    user = json.loads(response.content)
    return user


def zoom_get_users_by_type(client, user_type=LICENSED):
    all_users = zoom_get_all_users(client)
    users = []
    for user in all_users:
        if user['type'] == user_type:
            users.append(user)
    return users


def zoom_set_user_type(client, user_id, user_type):
    response = client.user.update(id=user_id, type=user_type)
    if response.status_code != 204:
        if user_type == LICENSED:
            suggestion = " (maybe no unused licenses available?)"
        else:
            suggestion = ""
        abort(f"could not update user '{user_id}' to type '{user_types[user_type]}'{suggestion}")
    return None


def abort(msg, exit_code=1):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
