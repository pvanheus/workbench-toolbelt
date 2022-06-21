import sys
from bioblend import toolshed

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]


# we can explicitly make assignments on it
# this.tool_name = None

# this.toolshed_name = 'toolshed.g2.bx.psu.edu'
# tool_name = 'read_it_and_keep'
# tool_author = 'iuc'
# tool_revision = '1563b58905f4'
# toolshed_url = f'https://{toolshed_name}'

def connect(tool_entry):
    ts = toolshed.ToolShedInstance(url=toolshed_url)
    return ts.repositories.get_repository_revision_install_info(tool_name, tool_author, tool_revision)


# def tools(result):
#     for dictionary in result:
#         if 'valid_tools' in dictionary:
#             spec_strs = []
#             # this dict contains a list of installable tools
#             for tool in dictionary['valid_tools']:
#                 print(tool['id'])
#                 for requirement in tool['requirements']:
#                     if 'version' in requirement:
#                         spec_str = f'{requirement["name"]}=={requirement["version"]}'
#                         spec_strs.append(spec_str)
#                         print(spec_str)
#                     else:
#                         print(f'unversioned {requirement["name"]}', file=sys.stderr)
#             print(','.join(spec_strs))

def connect():
    ts = toolshed.ToolShedInstance(url=toolshed_url)
    result = ts.repositories.get_repository_revision_install_info(
        tool_name, tool_author, tool_revision)
