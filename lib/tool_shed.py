import sys

import click
from bioblend import toolshed

# this is a pointer to the module object instance itself.
from loguru import logger

this = sys.modules[__name__]


def basic_metadata(tool_entry):
    ts = toolshed.ToolShedInstance(url=tool_entry['toolshed_url'])
    return ts.repositories.get_repository_revision_install_info(tool_entry['tool_name'], tool_entry['tool_author'],
                                                                tool_entry['tool_revision'])


def complete_metadata(tool):
    if not tool:
        logger.error(f"Error, no tool specified to fetch data")
        raise click.ClickException(f"Something went wrong: Tool not passed")

    meta_data = basic_metadata(tool)
    for meta in meta_data:
        if 'valid_tools' in meta:
            spec_strs = []
            # this dict contains a list of installable tools
            for tool in meta['valid_tools']:
                print(tool['id'])
                for requirement in tool['requirements']:
                    if 'version' in requirement:
                        spec_str = f'{requirement["name"]}=={requirement["version"]}'
                        spec_strs.append(spec_str)
                        print(spec_str)
                    else:
                        logger.error(f"Unversioned Error, no tool specified to fetch data. { requirement['name'] }")
            print(','.join(spec_strs))
