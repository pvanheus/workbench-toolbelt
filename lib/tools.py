import yaml, os
import sys

# from toolshed import complete_metadata

this = sys.modules[__name__]


def read_from_plugins(irida_plugin_path):
    file_names = [
        f
        for f in os.listdir(irida_plugin_path)
        if os.path.isfile(os.path.join(irida_plugin_path, f))
    ]

    tool_files = [get_fullpath_for_tool_yaml(f) for f in file_names]
    return [read_tool_set_file(file) for file in tool_files]


def get_fullpath_for_tool_yaml(file, irida_plugin_path):
    """path to the tool yaml file"""
    base_dir = os.path.join(
        irida_plugin_path, os.path.join(file + ".contents", "workflows/")
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


def install_gx_tools(plugins_tools):
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
