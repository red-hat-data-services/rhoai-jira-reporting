#! /usr/bin/env python3

import argparse
import os

from datetime import datetime, timedelta
from jira import JIRA
from utils import connect_to_jira, get_all_search_results, TARGET_PROJECT


DATETIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'


def parse_args():
    """Parse command line argments passed to the script"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token-file', required=True,
                        help='Path to a file containing the JIRA personal access token')
    parser.add_argument('-d', '--date', required=True,
                        help="The Target Date - format YYYY-MM-DD This should be the last day of the sprint")
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    return parser.parse_args()


def build_query(open_sprints):
    """
    Construct a Jira query string identifying all sprints active on the target date

    This function takes a list of sprints as input and returns a Jira query such as the following:
      sprint in ('Sprint 1', 'Sprint 2', 'Sprint 3')
    
    Arguments:
      open_sprints (list): A list of sprint names as strings
      
    Returns:
      A properly formatted Jira search string for identifying all issues in one of the specified sprints
    """
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


def get_sprints_open_on_date(jira, boards, target_date):
    """
    Get a list of sprints that were active on a specified target date
    
    This function iterates through all of the boards specified, identifes the boards that are Scrum
    boards (and therefore use sprints), and then identifies any sprints for that board that
    were active on a specified target date.
    
    Arguments:
      jira (JIRA):  A JIRA client object with an existing connection to the Jira server
      boards (list): A list of Board objects
      target_date (date): The date for which to identify active sprints

    Returns:
      A list of strings of sprint names that were active on the target date
    """
    sprints_open_on_date = []
    
    for b in boards:
        if b.type == 'scrum':
            sprints_for_board = jira.sprints(b.id)
            for s in sprints_for_board:
                if hasattr(s, 'startDate') and hasattr(s, 'completeDate') and s.name not in sprints_open_on_date:
                    start_date = datetime.strptime(s.startDate, DATETIME_FMT).date()
                    end_date = datetime.strptime(s.completeDate, DATETIME_FMT).date()
                    if start_date <= target_date <= end_date:
                        sprints_open_on_date.append(s.name)

    if not len(sprints_open_on_date):
        print('Something went wrong. No sprints were identified as active on the target date.')
        exit(1)

    return sprints_open_on_date


def print_results(verbose, applicable_sprints_query, total_issue_count,
                  sized_issue_count, completed_issues_count,
                  sized_issues_query, completed_issues_query):
    """
    Helper function to print out the formatted results
    
    This was split out to a helper function just to keep the main function a bit cleaner.
    """
    print(applicable_sprints_query)
    print(f'Total issues on applicable sprints: {total_issue_count}')
    print(f'Sized issues: {sized_issue_count}')
    print(f'Completed issues: {completed_issues_count}')

    if verbose:
        print('Queries used:')
        print('\tIssues in sprints query:')
        print(applicable_sprints_query)
        print('\tSized issues query:')
        print(sized_issues_query)
        print('\tCompleted issues query:')
        print(completed_issues_query)


def main():
    """
    Print data for the 2024 OpenShift AI Agile Excellence OKR
    
    Report on the number of issues assigned to a sprint for a specified date, the
    number of those issues with story points assigned, and the number of those issues
    completed by the end of the sprint
    """
    args = parse_args()

    # Construct a date object representing the target date for which to get metrics
    target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    
    # Create a Jira client connection
    jira = connect_to_jira(args.token_file)

    # Get all boards associated with the target Jira project
    boards_in_project = jira.boards(projectKeyOrID=TARGET_PROJECT)

    # For each board in the project, get a list of sprints that were active on the specified date
    sprints_open_on_date = get_sprints_open_on_date(jira, boards_in_project, target_date)
    if args.verbose:
        print('Applicable sprints:')
        print('\n'.join(sprints_open_on_date))

    # Construct the base Jira search query that will be used to identify issues for the applicable sprints
    applicable_sprints_query = build_query(sprints_open_on_date)
    print(applicable_sprints_query)

    # Get the total number of issues returned for the base query
    total_issue_count = jira.search_issues(applicable_sprints_query).total

    # Construct a Jira query for identifying issues with a story point estimate assigned
    sized_issues_query = f'{applicable_sprints_query} and "Story Points" is not empty'

    # Get the total number of issues with a story point estimate assigned
    sized_issue_count = jira.search_issues(sized_issues_query).total

    # Construct a date object that is one day after the specified target date.
    # By filtering issues that were complete before one day after the end of the sprint,
    # we effectively identify issues that were completed within the sprint.
    # *TODO* This logic should be reworked. A more robust solution would be to iterate
    # through each sprint, identify the end date of that sprint, then filter isseus that
    # were on that sprint and completed by that end date.
    completed_date = target_date + timedelta(days=1)

    # Construct a Jira query for identifying issues that were closed or resolved before the specified date
    completed_issues_query = f'{applicable_sprints_query} and (status changed to "Resolved" before "{completed_date}" or status changed to "Closed" before "{completed_date}")'
    
    # Get the total number of issues that were completed before the end of the sprint
    completed_issues_count = jira.search_issues(completed_issues_query).total

    # Print the results
    print_results(args.verbose, applicable_sprints_query, total_issue_count,
                  sized_issue_count, completed_issues_count,
                  sized_issues_query, completed_issues_query)


if __name__ == '__main__':
    main()