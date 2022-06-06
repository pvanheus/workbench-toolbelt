import os
import subprocess
import urllib
import yaml

import click
from decouple import config
from github import Github, GithubException
from loguru import logger
from tqdm.auto import tqdm

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
    to auto install and update
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
    # get the plugin assets (jars)
    for repo in g.get_organization("combat-sars-cov-2").get_repos():
        version = plugin_versions.get(repo.name, None)
        if version:
            release = None
            if version == "latest":
                try:
                    release = repo.get_latest_release()
                except GithubException as e:
                    logger.error(
                        "Error, seems we can't find the latest release package"
                    )
                    raise click.ClickException(f"Something went wrong: {repr(e)}")
            else:
                try:
                    release = repo.get_release(version)
                except GithubException as e:
                    logger.error(
                        f"Error, seems we can't find {version} release package"
                    )
                    raise click.ClickException(f"Something went wrong: {repr(e)}")

            if release is None:
                raise click.ClickException("Something went wrong: release is not found")

            logger.info(f"Download begin for plugin package: {release.url.encode()}")
            for asset in release.get_assets():
                logger.info(f"IRIDA Plugin Jar: {asset.browser_download_url}")

                response = getattr(urllib, "request", urllib).urlopen(
                    asset.browser_download_url
                )
                file_name = os.path.join(CURRENT_DIR, f"sources/plugins/{asset.name}")

                ensure_dir(file_name)
                with tqdm.wrapattr(
                    open(file_name, "wb"),
                    "write",
                    miniters=1,
                    desc=asset.browser_download_url.split("/")[-1],
                    total=getattr(response, "length", None),
                ) as fout:
                    for chunk in response:
                        fout.write(chunk)
            logger.info(f"Downloading is done: {release.url.encode()}")


def ensure_dir(file_path):
    """
    Directory - ensure that directory if it exists
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


@workbench.command()
def extract_jar():
    """
    This command extracts the jar packaged plugin to
    relevant folder structures to be processed later
    """
    # file_names from arguments
    file_names = [
        f
        for f in os.listdir(PATH_TO_PLUGINS)
        if os.path.isfile(os.path.join(PATH_TO_PLUGINS, f))
    ]
    for file_name in file_names:
        unzip(file_name)


def unzip(file_name):
    """
    Unzip the JAR/ZIP plugins
    """
    o_dir = get_expanded_dir_name(file_name)
    ensure_dir(o_dir)

    logger.info(f"Processing: {file_name} into: {o_dir}")

    command = f"unzip {os.path.join(PATH_TO_PLUGINS, file_name)} -d {o_dir}"
    process = subprocess.Popen(command, shell=True)
    status = os.waitpid(process.pid, 0)[1]

    walk_files(o_dir)


def walk_files(dir_name):
    """
    Walk through the files in the targeted directory
    """
    logger.info(f"Walking the files of {dir_name}")

    dirs = os.walk(dir_name)

    for (dir_path, dir_names, file_names) in dirs:
        for file_name in file_names:
            if is_archive(file_name):
                unzip(os.path.join(dir_path, file_name))


def is_archive(file_name):
    """
    Check if the extension of (file) is valid
    """
    ext = file_name[-4:]
    if ext in [".jar"]:
        return True
    return False


def get_expanded_dir_name(file_name):
    """
    Get the expanded directory name
    """
    base_name = f"{os.path.basename(file_name)}.contents"
    return os.path.join(PATH_TO_PLUGINS, base_name)


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
    logger.info("Make the singularity magic happen")
    file_names = [
        f
        for f in os.listdir(PATH_TO_PLUGINS)
        if os.path.isfile(os.path.join(PATH_TO_PLUGINS, f))
    ]

    tool_files = [get_fullpath_for_tool_yaml(f) for f in file_names]
    plugins_tools = [read_tool_set_file(file) for file in tool_files]

    # run the ephemiris tool to install tools
    for tools in plugins_tools:
        for t in tools:
            try:
                command = (
                    f'shed-tools install -g {galaxy} -a "{api_key}" -u "{user}" -p "{password}" --toolshed {t["tool_shed_url"]} --skip_install_resolver_dependencies '
                    f'--skip_install_repository_dependencies --name "{t["name"]}" --owner "{t["owner"]}" --revisions {" ".join(t["revisions"])} --section_label "{t["tool_panel_section_label"]}"'
                )
                process = subprocess.Popen(command, shell=True)
                status = os.waitpid(process.pid, 0)[1]
            except Exception as e:
                logger.error(f"Error, while trying to install {t['name']}")
                raise click.ClickException(f"Something went wrong: {repr(e)}")


def get_fullpath_for_tool_yaml(file):
    """path to the tool yaml file"""
    base_dir = os.path.join(
        PATH_TO_PLUGINS, os.path.join(file + ".contents", "workflows/")
    )
    dirs = os.walk(base_dir)
    dd = [dir_names for dir_names in sorted(dirs)]
    return os.path.join(dd[-1][0], "tools.yaml")


def read_tool_set_file(tool_file):
    """
    Read the tool.yaml file
    """
    with open(tool_file) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        return [t for t in yaml.load(file, Loader=yaml.FullLoader)["tools"]]


@workbench.command()
def install_wf():
    """
    This command installs the workflow in galaxy
    """
    pass


if __name__ == "__main__":
    workbench()
