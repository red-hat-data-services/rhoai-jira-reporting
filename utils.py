import os

from jira import JIRA
from tqdm import tqdm

JIRA_SERVER_URL = 'https://issues.redhat.com'
TARGET_PROJECT = 'RHOAIENG'


def connect_to_jira(token_file_path):
    """
    Create a JIRA client object connected to the Jira server

    Arguments:
      token_file_path (str): The path to a file containing the Jira personal access token
    
    Returns:
      A JIRA client object authenticated to the Jira server
    """
    assert os.path.exists(token_file_path)
    with open(token_file_path) as f:
        token = f.read().strip()

    return JIRA(JIRA_SERVER_URL, token_auth=token)


def get_all_search_results(jira_client, query, fields=None):
    """
    Run a given Jira query and return all results as a python list

    The python Jira client uses pagination to fetch Jira queries with a
    large number of results. This requires iterating through the pages of
    search results. This function handles this pagination, collating
    all results into a single python list.

    Arguments:
      jira_client (JIRA): A JIRA client object with an existing connection to the Jira server
      query (str): The jira search string
      fielts (list): An optional list of Jira fields to include in the results
    
    Returns:
      A list of Jira search results
    """
    results = []
    i = 0
    chunk_size = 100

    progress_bar = None

    while True:
        chunk = jira_client.search_issues(query, startAt=i, maxResults=chunk_size, fields=fields)
        if not progress_bar:
            progress_bar = tqdm(total=(chunk.total // chunk_size) + 1)
        i += chunk_size
        results += chunk.iterable
        progress_bar.update(1)

        if i >= chunk.total:
            break

    return results