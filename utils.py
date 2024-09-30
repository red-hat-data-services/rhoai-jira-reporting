from tqdm import tqdm


def get_all_search_results(jira_client, query, fields=None):
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