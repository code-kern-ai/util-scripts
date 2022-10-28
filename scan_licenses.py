import requests
import json
import os
import pandas as pd
from contextlib import contextmanager

from licensecheck import get_deps, formatter

UPDATE_DOWNLOAD_URLS = False
DOWNLOAD_REQUIREMENTS = False
DIR_REQUIREMENTS_FILES = os.path.realpath("requirements_files/{repo}/requirements.txt")

download_urls = {
    "automl-docker": "https://raw.githubusercontent.com/code-kern-ai/automl-docker/dev/requirements.txt",
    "datalift-summit": "https://raw.githubusercontent.com/code-kern-ai/datalift-summit/dev/requirements.txt",
    "embedders": "https://raw.githubusercontent.com/code-kern-ai/embedders/dev/requirements.txt",
    "refinery": "https://raw.githubusercontent.com/code-kern-ai/refinery/main/requirements.txt",
    "refinery-authorizer": "https://raw.githubusercontent.com/code-kern-ai/refinery-authorizer/dev/requirements.txt",
    "refinery-config": "https://raw.githubusercontent.com/code-kern-ai/refinery-config/dev/requirements.txt",
    "refinery-doc-ock": "https://raw.githubusercontent.com/code-kern-ai/refinery-doc-ock/dev/requirements.txt",
    "refinery-embedder": "https://raw.githubusercontent.com/code-kern-ai/refinery-embedder/dev/requirements.txt",
    "refinery-gateway": "https://raw.githubusercontent.com/code-kern-ai/refinery-gateway/dev/requirements.txt",
    "refinery-gateway-proxy": "https://raw.githubusercontent.com/code-kern-ai/refinery-gateway-proxy/dev/requirements.txt",
    "refinery-lf-exec-env": "https://raw.githubusercontent.com/code-kern-ai/refinery-lf-exec-env/dev/requirements.txt",
    "refinery-ml-exec-env": "https://raw.githubusercontent.com/code-kern-ai/refinery-ml-exec-env/dev/requirements.txt",
    "refinery-neural-search": "https://raw.githubusercontent.com/code-kern-ai/refinery-neural-search/dev/requirements.txt",
    "refinery-python-sdk": "https://raw.githubusercontent.com/code-kern-ai/refinery-python-sdk/master/requirements.txt",
    "refinery-record-ide-env": "https://raw.githubusercontent.com/code-kern-ai/refinery-record-ide-env/dev/requirements.txt",
    "refinery-tokenizer": "https://raw.githubusercontent.com/code-kern-ai/refinery-tokenizer/dev/requirements.txt",
    "refinery-updater": "https://raw.githubusercontent.com/code-kern-ai/refinery-updater/dev/requirements.txt",
    "refinery-weak-supervisor": "https://raw.githubusercontent.com/code-kern-ai/refinery-weak-supervisor/dev/requirements.txt",
    "refinery-zero-shot": "https://raw.githubusercontent.com/code-kern-ai/refinery-zero-shot/dev/requirements.txt",
    "sequence-learn": "https://raw.githubusercontent.com/code-kern-ai/sequence-learn/main/requirements.txt",
    "weak-nlp": "https://raw.githubusercontent.com/code-kern-ai/weak-nlp/dev/requirements.txt",
}

if UPDATE_DOWNLOAD_URLS:
    # public repos
    # get list from github api
    url_github_api = "https://api.github.com/users/code-kern-ai/repos"
    repos = requests.get(url_github_api).json()
    # extract repo links
    repo_names = [repo["name"] for repo in repos]
    # try to download requirements.txt
    # assumes that the file is placed on top-level
    download_urls = {}
    for repo in repo_names:
        requirements_urls = f"https://api.github.com/repos/code-kern-ai/{repo}/contents/requirements.txt"
        response = requests.get(requirements_urls)
        if response.status_code != 200:
            print(f"Error for repository {repo}")
            print(response.content)
            continue
        download_urls[repo] = response.json()["download_url"]

if DOWNLOAD_REQUIREMENTS:
    # download requirements files
    for repo, url in download_urls.items():
        requirements = requests.get(url).text
        requirements_path = DIR_REQUIREMENTS_FILES.format(repo=repo)
        os.makedirs(os.path.dirname(requirements_path), exist_ok=True)
        with open(requirements_path, "w") as f:
            f.write(requirements)


@contextmanager
def working_directory(path):
    """
    A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    Usage:
    > # Do something in original directory
    > with working_directory('/my/new/path'):
    >     # Do something in new directory
    > # Back to old directory
    """

    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


for repo in download_urls:
    requirements_dir = os.path.dirname(DIR_REQUIREMENTS_FILES.format(repo=repo))
    filename = os.path.join(requirements_dir, "licenses.json")
    with working_directory(requirements_dir):
        dependenciesWLicenses = get_deps.getDepsWLicenses(
            "requirements", [], [], [], []
        )
        with open(filename, "w") as f:
            print(
                formatter.formatMap["json"](dependenciesWLicenses),
                file=f,
            )

for repo in download_urls:
    requirements_dir = os.path.dirname(DIR_REQUIREMENTS_FILES.format(repo=repo))
    filename = os.path.join(requirements_dir, "licenses.json")
    with open(filename, "r") as f:
        data = json.load(f)

    table_path = os.path.join(requirements_dir, "licenses.xlsx")
    table = [[package["name"], package["license"]] for package in data["packages"]]
    df = pd.DataFrame(table)
    df.to_excel(table_path)

# overview table
all_licenses = {}
for repo in download_urls:
    if repo in ["automl-docker", "datalift-summit"]:
        continue

    requirements_dir = os.path.dirname(DIR_REQUIREMENTS_FILES.format(repo=repo))
    filename = os.path.join(requirements_dir, "licenses.json")
    with open(filename, "r") as f:
        data = json.load(f)

    for package in data["packages"]:
        if package["name"] not in all_licenses:
            all_licenses[package["name"]] = package["license"]

list_all_licenses = [[key, all_licenses[key]] for key in sorted(all_licenses)]
df = pd.DataFrame(list_all_licenses)
df.to_excel("/Users/felixkirsch/Code/license_scanner/licenses_overview.xlsx")
