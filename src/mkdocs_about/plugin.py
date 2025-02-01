# ruff: noqa: D101, D103
import logging
from dataclasses import dataclass
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader, Template
from mkdocs.config import config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files

from mkdocs_about.template import DEFAULT_TEMPLATE

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class AboutPageConfig(c.Config):
    username = c.Type(str)
    header = c.Optional(c.Type(str))
    custom_template = c.Optional(c.Type(str))
    related = c.ListOfItems(c.Type(str), default=[])
    # related_external = c.ListOfItems(c.Type(str), default=[])  # noqa: ERA001
    exclude = c.ListOfItems(c.Type(str), default=[])


@dataclass(frozen=True)
class Repo:
    name: str
    url: str
    description: str


class AboutPagePlugin(BasePlugin[AboutPageConfig]):
    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> None:  # noqa: D102
        current_project = get_current_project_name(
            repo_url=config.repo_url,
        )

        repos = get_repos(username=self.config.username)
        repos = exlcude_repos(
            exclude=[*self.config.exclude, current_project], repos=repos
        )
        related_projects, other_projects = split_repos(
            related=self.config.related, repos=repos
        )

        template = get_template(custom_template=self.config.custom_template)
        content = template.render(
            header=self.config.header,
            related_projects=related_projects,
            other_projects=other_projects,
        )

        files.append(File.generated(config=config, src_uri="about.md", content=content))


def exlcude_repos(exclude: list[str], repos: list[Repo]) -> list[Repo]:
    if not exclude:
        return repos
    return [repo for repo in repos if repo.name not in exclude]


def split_repos(related: list[str], repos: list[Repo]) -> tuple[list[Repo], list[Repo]]:
    related_projects: list[Repo] = []
    other_projects: list[Repo] = []

    for repo in repos:
        if repo.name in related:
            related_projects.append(repo)
        else:
            other_projects.append(repo)

    return related_projects, other_projects


def get_repos(username: str) -> list[Repo]:
    response = requests.get(
        url=f"https://api.github.com/users/{username}/repos", timeout=15
    )
    response.raise_for_status()
    repos = response.json()

    if not isinstance(repos, list):
        msg = "Expected GitHub API to respond with type `list`"
        raise TypeError(msg)

    return [
        Repo(
            name=repo.get("name"),
            url=repo.get("html_url"),
            description=repo.get("description"),
        )
        for repo in repos
        if not repo.get("fork")
    ]


def get_template(custom_template: str | None) -> Template:
    if not custom_template:
        return Template(DEFAULT_TEMPLATE)

    template_path = Path(custom_template)

    if not template_path.exists():
        msg = "Custom template not found"
        raise FileNotFoundError(msg)

    template_dir = template_path.parent
    template_name = template_path.name

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )
    return env.get_template(template_name)


def get_current_project_name(repo_url: str | None) -> str:
    if not repo_url:
        name = __name__
        log.warning("`repo_url` not defined. Using %s", name)
    else:
        name = repo_url.split("/")[-1]
    return name
