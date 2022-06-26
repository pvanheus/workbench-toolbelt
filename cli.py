import os
import subprocess
import click

from decouple import config
from github import Github, GithubException
from loguru import logger
from lib.tools import read_from_plugins, install_gx_tools
from lib.tool_shed import complete_metadata
from lib.utils import ensure_dir, download_plugin_assets, extract_plugin_jars

CONTEXT_SETTINGS = dict(
    default_map={
        "download_jar": {
            "illumina_version": config("ILLUMINA_VERSION", default="latest"),
            "nanopore_version": config("NANOPORE_VERSION", default="latest"),
            "access_token": config("GITHUB_ACCESS_TOKEN", default=False),
        }
    }
)

CURRENT_DIR = os.path.dirname(__file__)
PATH_TO_PLUGINS = os.path.join(CURRENT_DIR, f"sources/plugins/")


@click.group(context_settings=CONTEXT_SETTINGS)
def workbench():
    """SARS-COV-2 Workbench (irida, galaxy ) utility scripts

    Group of utility commands
    to install and update
    workbench tools and workflows.
    support@sanbi.ac.za - for any issues
    \f

    :param click.core.Context ctx: Click context.
    """
    pass


@workbench.command()
@click.option(
    "--illumina-version", default="latest", help="Illumina (SARS-COV-2) release version"
)
@click.option(
    "--nanopore-version", default="latest", help="Nanopore (SARS-COV-2) release version"
)
@click.option("--access-token", help="Your unexpired & valid github access token")
def download_jar(illumina_version, nanopore_version, access_token):
    """
    This command downloads the workbench plugins from github
    Note: Default version is latest package release
    """
    try:
        g = Github(access_token)
    except GithubException as e:
        logger.error("Github token is missing or invalid")
        raise click.ClickException(f"Something went wrong: {repr(e)}")

    plugin_versions = {
        "irida-plugin-sars-cov-2-illumina": illumina_version,
        "irida-plugin-sars-cov-2-nanopore": nanopore_version,
    }
    download_plugin_assets(g, plugin_versions)

@workbench.command()
def extract_jar():
    """
    This command extracts the jar packaged plugin to
    relevant folder structures to be processed later
    """
    # file_names from arguments
    extract_plugin_jars()

@workbench.command()
def deploy_plugin():
    """
    This command deploys the jar plugin to the targeted irida instance
    """
    pass


@workbench.command()
@click.option(
    "--galaxy", default="http://nginx:90", help="The targeted Galaxy instance"
)
@click.option(
    "--user",
    default="admin@galaxy.org",
    help="The username to use accessing the galaxy instance",
)
@click.option("--password", default="password", help="Password for the user")
@click.option(
    "--api-key", default="fakekey", help="API Key token generated for the user"
)
def install_tools(galaxy, user, password, api_key):
    """
    This command installs the tools in galaxy
    """
    logger.info("Install to Galaxy Instance")
    plugins_tools = read_from_plugins(PATH_TO_PLUGINS)
    install_gx_tools(plugins_tools)


@workbench.command()
@click.option(
    "--illumina-version", default="latest", help="Illumina (SARS-COV-2) release version"
)
@click.option(
    "--nanopore-version", default="latest", help="Nanopore (SARS-COV-2) release version"
)
@click.option("--access-token", help="Your unexpired & valid github access token")
def build_images(illumina_version, nanopore_version, access_token):
    """
    Build Singularity Images from a Galaxy Workflow file.
    :return: status
    """
    try:
        g = Github(access_token)
    except GithubException as e:
        logger.error("Github token is missing or invalid")
        raise click.ClickException(f"Something went wrong: {repr(e)}")

    plugin_versions = {
        "irida-plugin-sars-cov-2-illumina": illumina_version,
        'irida-plugin-sars-cov-2-nanopore': nanopore_version,
    }
    # download plugins
    download_plugin_assets(g, plugin_versions)

    # unpack the jar files
    extract_plugin_jars()

    tool_list = read_from_plugins(PATH_TO_PLUGINS)
    for tools in tool_list:
        for t in tools:
            try:
                data = complete_metadata(t)
                print(data)
            except Exception as e:
                logger.error(f"Error, while trying to build image for tool {t['name']}")
                raise click.ClickException(f"Something went wrong: {repr(e)}")

@workbench.command()
def install_workflows():
    """
    This command installs the workflow in galaxy
    """
    pass


if __name__ == "__main__":
    workbench()
