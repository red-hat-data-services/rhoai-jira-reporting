#! /usr/bin/env python3

import argparse
import os

from jira import JIRA
from tqdm import tqdm
from utils import connect_to_jira, get_all_search_results


def parse_args():
    """Parse command line argments passed to the script"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    return parser.parse_args()


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


def main():
    """
    Identify issues linked to a RHOAI feature or initiative

    Identifies all Features and Initiatives in RHOAISTRAT or RHOAIENG, respectively,
    then prints the identifier for all issues related to one of these.
    """
    args = parse_args()
    jira = connect_to_jira(args.token_file)


    issues_in_parents = set(get_issues_in_features_and_initiatives(jira))
    print(issues_in_parents)


if __name__ == '__main__':
    main()