#!/usr/bin/env python3

import argparse
import sys

import yaml


def write_yaml(name: str, requirements: dict[str, str], channels: list[str] =None) -> str:
    output_dict = {}
    output_dict['name'] = name
    if channels is not None:
        output_dict['channels'] = [ channel_name for channel_name in channels.split(',') ]
    requirement_list = []
    for (package_name, value) in requirements.items():
        requirement_list.append(f'{package_name}={value}')
    output_dict['dependencies'] = requirement_list
    return yaml.dump(output_dict, sort_keys=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--channels')
    parser.add_argument('--exclude', '-X')
    parser.add_argument('name', help='Environment name')
    parser.add_argument('requirements_file', type=argparse.FileType())
    parser.add_argument('output_file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    excluded_packages = []
    requirements = {}
    packages_to_exclude = set()
    if args.exclude is not None:
        packages_to_exclude = set(args.exclude.split(','))
    for line in args.requirements_file:
        if line.startswith('#'):
            continue
        (package_name, version) = line.rstrip().split('==')
        if package_name not in packages_to_exclude:
            requirements[package_name] = version
        else:
            excluded_packages.append((package_name, version))
    
    yaml_str = write_yaml(args.name, requirements, args.channels)
    if excluded_packages:
        yaml_str += '\n# packages excluded\n'
        yaml_str += '\n'.join([ f'#{package_name}=={version}' for (package_name, version) in excluded_packages ])
        yaml_str += '\n'
    args.output_file.write(yaml_str)

