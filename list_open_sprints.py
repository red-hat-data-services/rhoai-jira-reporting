#! /usr/bin/env python3

import argparse
import os

from jira import JIRA
from utils import get_all_search_results


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    return parser.parse_args()


def build_query(open_sprints):
    query = 'sprint in ('
    first = True
    for s in open_sprints:
        if not first:
            query += f", '{s}'"
        else:
            query += f"'{s}'"
            first = False
    query += ")"
    return query


def main():
    args = parse_args()
    assert os.path.exists(args.token_file)
    with open(args.token_file) as f:
        token = f.read().strip()

    jira = JIRA('https://issues.redhat.com', token_auth=token)

    boards_in_project = jira.boards(projectKeyOrID='RHOAIENG')
    active_sprints = []
    for b in boards_in_project:
        if b.type == 'scrum':
            sprints_for_board = jira.sprints(b.id)
            for s in sprints_for_board:
                if s.state == 'active':
                    active_sprints.append(s.name)
    print(build_query(active_sprints))


if __name__ == '__main__':
    main()