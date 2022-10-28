Creates an overview of the licenses of the packages used by the public repositories of
code-kern-ai.

To use follow the following steps:
1. install requirements with: pip install -r requirements.txt
2. run the script with: python scan_licenses.py

Running the script, creates/updates the license tables/json files for each repository.
These are located in requirement-files. An overview, containing all dependencies
together, is created inside this directory: licenses_overview.xlsx.