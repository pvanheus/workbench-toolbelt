import os
import urllib
import click

from loguru import logger
from tqdm.auto import tqdm

CURRENT_DIR = os.path.dirname(__file__)
PATH_TO_PLUGINS = os.path.join(CURRENT_DIR, f"sources/plugins/")


def ensure_dir(file_path):
    """
    Directory - ensure that directory if it exists
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


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


def download_plugin_assets(g, plugin_versions):
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


def extract_plugin_jars():
    file_names = [
        f
        for f in os.listdir(PATH_TO_PLUGINS)
        if os.path.isfile(os.path.join(PATH_TO_PLUGINS, f))
    ]
    for file_name in file_names:
        unzip(file_name)



