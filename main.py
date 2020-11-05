import argparse
import logging
from typing import Dict
import requests
from requests import Response
from jinja2 import Template

GITLAB_ADDRESS = "https://gitlab.example.com"
GITLAB_ADDRESS_API = f"{GITLAB_ADDRESS}/api/v4"
GITLAB_TOKEN = "<your_private_token>"

report_template = """
<html>
<body>
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  overflow:hidden;padding:10px 5px;word-break:normal;}
.tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
.tg .tg-0lax{text-align:left;vertical-align:top}
</style>
The report for {{ report_server }}.\n
<table class="tg">
<tbody>
{% for project_id, project_data in projects.items() %}
  <tr>
    <th class="tg-0pky" colspan="2">{{ project_data["name"] }} ({{ project_id }})</th>
  </tr>
{% if "repositories" in project_data %}
    {% for repo_id, repo_data in project_data["repositories"].items() %}
  <tr>
    <td class="tg-0pky">{{ repo_data["name"] }} ({{ repo_id }})</td><td class="tg-0pky">{{ repo_data["tags_count"] }}</td>
  </tr>
{% endfor %}
{% endif %}
{% endfor %}
</tbody>
</table>
</body>
</html>
"""


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, help="Address of your Gitlab server, with proto (http or https)",
                        required=True, default="https://gitlab.example.com")
    parser.add_argument("-t", "--token", type=str, help="Your private API token to your Gitlab server",
                        required=True)
    parser.add_argument("-l", "--level", type=str, help="Log level",
                        required=False, default="INFO")

    return parser.parse_args()


def configure_logger(log_level="INFO"):
    log_level = log_level.upper()
    if log_level in logging._nameToLevel:
        level = logging._nameToLevel.get(log_level)
        logger = logging.getLogger()
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s [%(filename)s.%(lineno)d] %(processName)s %(levelname)-1s %(name)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # fh = logging.FileHandler('gitlab_registry_reporter.log')
        # fh.setLevel(level)
        # fh.setFormatter(formatter)
        # logger.addHandler(fh)
    else:
        raise Exception(f"Can't recognize log level: {log_level}")


def get_request(tail: str) -> Response:
    logging.debug("get_url: %s", f"{GITLAB_ADDRESS_API}{tail}")
    return requests.get(f"{GITLAB_ADDRESS_API}{tail}", headers={"PRIVATE-TOKEN": GITLAB_TOKEN})


def get_projects() -> Dict:
    result: Dict = dict()
    projects_raw = get_request("/projects?pagination=keyset&per_page=50000&order_by=id&sort=asc")
    if projects_raw.status_code == 200:
        for project in projects_raw.json():
            result[project["id"]] = {"name": project["name_with_namespace"]}
        return result
    else:
        logging.error("Can't get information about projects at this server.")
        return dict()


def get_repositories(projects: Dict):
    for project_id, project_data in projects.items():
        response_raw = get_request(f"/projects/{project_id}/registry/repositories?tags_count=true")
        if response_raw.status_code == 200:
            response = response_raw.json()
            repository: Dict = dict()
            for repository_raw in response:
                repository_id = repository_raw["id"]
                repository_data: Dict = dict()
                tag_count = repository_raw["tags_count"]
                repository_data["name"] = repository_raw["name"]
                repository_data["tags_count"] = tag_count
                repository[repository_id] = repository_data
            project_data["repositories"] = repository
            logging.debug(project_data)
        else:
            logging.error("Can't get information about repository")



def generate_report(projects):
    if len(projects) > 0:
        tm = Template(report_template)
        msg = tm.render(report_server=GITLAB_ADDRESS, projects=projects)
        with open('report.html', 'w') as data:
            data.write(msg)
    else:
        logging.error("Can't generate report, project list is empty")


def main():
    logging.info("Get list of repositories")
    projects = get_projects()
    if len(projects) > 0:
        logging.info("Receive information about registries")
        get_repositories(projects)
        logging.info("Generate report")
        generate_report(projects)
        logging.info("Done!")
    else:
        logging.error("Project list is empty. Check address of Gitlab server and token.")


if __name__ == '__main__':
    args = read_args()
    GITLAB_ADDRESS: str = args.server
    GITLAB_ADDRESS_API: str = f"{GITLAB_ADDRESS}/api/v4"
    GITLAB_TOKEN: str = args.token
    configure_logger(args.level)
    logging.info("Gitlab address - %s", GITLAB_ADDRESS)
    logging.info("Gitlab address API - %s", GITLAB_ADDRESS_API)
    logging.info("Gitlab token - %s...", GITLAB_TOKEN[:5])
    main()
