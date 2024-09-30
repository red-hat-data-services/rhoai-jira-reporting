#! /usr/bin/env python3

import argparse
import os

from datetime import datetime, timedelta
from jira import JIRA
from utils import get_all_search_results


DATETIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    parser.add_argument('-d', '--date', required=True,
                        help="The Target Date - format YYYY-MM-DD ")
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
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

    target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    jira = JIRA('https://issues.redhat.com', token_auth=token)

    boards_in_project = jira.boards(projectKeyOrID='RHOAIENG')
    sprints_open_on_date = []
    for b in boards_in_project:
        if b.type == 'scrum':
            sprints_for_board = jira.sprints(b.id)
            for s in sprints_for_board:
                if hasattr(s, 'startDate') and hasattr(s, 'completeDate') and s.name not in sprints_open_on_date:
                    start_date = datetime.strptime(s.startDate, DATETIME_FMT).date()
                    end_date = datetime.strptime(s.completeDate, DATETIME_FMT).date()
                    if start_date <= target_date <= end_date:
                        sprints_open_on_date.append(s.name)
    if args.verbose:
        print('Applicable sprints:')
        print('\n'.join(sprints_open_on_date))
    applicable_sprints_query = (build_query(sprints_open_on_date))
    print(applicable_sprints_query)
    total_issue_count = jira.search_issues(applicable_sprints_query).total

    sized_issues_query = f'{applicable_sprints_query} and "Story Points" is not empty'
    sized_issue_count = jira.search_issues(sized_issues_query).total

    completed_date = target_date + timedelta(days=1)
    completed_issues_query = f'{applicable_sprints_query} and (status changed to "Resolved" before "{completed_date}" or status changed to "Closed" before "{completed_date}")'
    completed_issues_count = jira.search_issues(completed_issues_query).total

    print(applicable_sprints_query)
    print(f'Total issues on applicable sprints: {total_issue_count}')
    print(f'Sized issues: {sized_issue_count}')
    print(f'Completed issues: {completed_issues_count}')

    if args.verbose:
        print('Queries used:')
        print('\tIssues in sprints query:')
        print(applicable_sprints_query)
        print('\tSized issues query:')
        print(sized_issues_query)
        print('\tCompleted issues query:')
        print(completed_issues_query)


if __name__ == '__main__':
    main()