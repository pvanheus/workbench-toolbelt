import yaml, os
import sys

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

def toolshed_meta(result):
    for dictionary in result:
        if 'valid_tools' in dictionary:
            spec_strs = []
            # this dict contains a list of installable tools
            for tool in dictionary['valid_tools']:
                print(tool['id'])
                for requirement in tool['requirements']:
                    if 'version' in requirement:
                        spec_str = f'{requirement["name"]}=={requirement["version"]}'
                        spec_strs.append(spec_str)
                        print(spec_str)
                    else:
                        print(f'unversioned {requirement["name"]}', file=sys.stderr)
            print(','.join(spec_strs))