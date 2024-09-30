#! /usr/bin/env python3

import argparse
import os

from jira import JIRA
from tqdm import tqdm
from utils import get_all_search_results


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    return parser.parse_args()


def get_features_and_initiatives(jira):
    query = '(project=rhoaistrat and type = Feature) or (project=rhoaieng and type=Initiative)'
    return get_all_search_results(jira, query, ['id'])


def get_issues_in_parent(jira, parent_key):
    query = f'issue in childIssuesOf({parent_key})'
    return get_all_search_results(jira, query)


def get_issues_in_features_and_initiatives(jira):
    query = '(project=rhoaistrat and type = Feature) or (project=rhoaieng and type=Initiative)'
    parents = get_all_search_results(jira, query, ['id'])

    print('Generating list of all child keys for all features and initiatives...')
    issues_in_parents = []
    for parent in parents:
        children = get_issues_in_parent(jira, parent.key)
        issues_in_parents.extend([child.key for child in children])

    return issues_in_parents


def get_completed_issues_for_time_range(jira, start_date, end_date):
    query = ('project=rhoaieng '
             'and type = Story '
             'and statusCategory = Done '
             'and ('
             f'((status changed to Resolved after "{start_date}") and (status changed to Resolved before "{end_date}")) or '
             f'((status changed to Closed after "{start_date}") and (status changed to Closed before "{end_date}")))'
            )
    print(f'Running query {query}')
    completed_issues = get_all_search_results(jira, query)
    return [issue.key for issue in completed_issues]


def main():
    args = parse_args()
    assert os.path.exists(args.token_file)
    with open(args.token_file) as f:
        token = f.read().strip()

    start_date = '2024/01/01'
    end_date = '2024/06/01'

    jira = JIRA('https://issues.redhat.com', token_auth=token)

    # First
    print(f'Getting list of all issues completed between {start_date} and {end_date}')
    completed_issues = set(get_completed_issues_for_time_range(jira, start_date, end_date))
    with open('completed_issues.txt', 'w') as f:
        f.write('\n'.join(completed_issues))
        print(f'Wrote list of all completed issues to "completed_issues.txt"')


    issues_in_parents = set(get_issues_in_features_and_initiatives(jira))
    completed_issues_without_parent = completed_issues - issues_in_parents

    with open('results.txt', 'w') as f:
        f.write('\n'.join(completed_issues_without_parent))

    print(f'Between {start_date} and {end_date}, {len(completed_issues)} stories were completed.')
    print(f'Of these, {len(completed_issues_without_parent)} were not linked to a feature or initiative.')


if __name__ == '__main__':
    main()