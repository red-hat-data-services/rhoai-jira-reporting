# OpenShift AI Jira Reporting

This repository contains scripts for reporting on various agile metrics for the OpenShift
AI team, pulling data from Red Hat's Jira instance as the source of truth. Scripts use
the [Jira]https://pypi.org/project/jira/] python library for interacting with the
Jira API.

## Setup and Prerequisites

Before you can use the scripts in this repo, make sure you've met the
following prerequisites:

### Jira Personal Access Token

You will need to create a personal access token in Red Hat's Jira
instance so that the script can authenticate to the Jira API. Follow
the instructions [here](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) for
creating a token (under the `Creating PATs in the application` section).

Save the token in a file on your laptop, and keep track of the path to
this file. You'll pass this path as an input argument to the scripts later.
We'll refer to the path to this token file below as `$PATH_TO_TOKEN`.

### Python Dependencies

The scripts here depend on a few different python dependencies (most importantly
the Jira package). We use [Pipenv](https://pipenv.pypa.io/en/latest/0) to manage
these dependencies. Follow the instructions [here](https://pipenv.pypa.io/en/latest/installation.html)
to install Pipenv in your environment.

## Usage

Below we outline the various scripts in this repo and their usage

### 2024_okr1_report.py

This script is used to measure the various agile metrics tracked as part of
the OpenShift AI Engineering 2024 OKRs. This script will:

* Identify all sprints within the RHOAIENG Jira project that are active on
  a specified date
* Output the total number of issues assinged to any sprint that was active on the
  specified date
* Of the total number of issues, output the number of issues that had a story point
  estimate assigned
* Output the number of issues that were completed by the end date of the sprint **todo** The logic
  for determining the end date of a sprint is weak and is an area of future improvement.

To use this script, run the following: (you should provide the date for
which you're interested in the format `yyyy-mm-dd`) (**Important** The target date should be the last day of the sprint)
```
pipenv shell
pipenv install
python 2024_okr1_report.py -t $PATH_TO_TOKEN -d $TARGET_DATE
```

### issues_in_features_initiatives.py

This script is used to print out a list of all Jira issues related to a
RHOAI Feature or Inititative. This script is not typically used, but was
kept in this repo for reference purposes.

To use this script, run the following:
```
pipenv shell
pipenv install
python issues_in_features_initiatives.py -t $PATH_TO_TOKEN
```

### Helper Functions

There are various general-purpose functions shared across scripts in this
repository. For clean reusability, we consolidate these functions in
[utils.py](utils.py). Individual helper functions are documented via comments
in that file.