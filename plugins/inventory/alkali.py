import ansible
import itertools
import os
import re
import yaml


def read_yaml(filename):

    result = {}
    config = yaml.load(open(filename))
    for host, config in config['hosts'].items():

        groups = config['groups']
        if type(groups) == str:
            groups = [groups]

        result[host] = {
            'groups': groups,
            'vars':   config.get('vars', {})
            }

    return result


class InventoryModule(ansible.plugins.inventory.BaseInventoryPlugin):

    def parse(self, inventory, loader, host_list, cache=True):

        super(InventoryModule, self).parse(inventory, loader, host_list)

        config = read_yaml(host_list)

        groups = set()
        for host_config in config.values():
            for group in host_config['groups']:
                groups.add(group)

        for group in groups:
            self.inventory.add_group(group)

        for host, host_config in config.items():

            for group in host_config['groups']:
                self.inventory.add_host(host, group)

            for k, v in host_config['vars'].items():
                self.inventory.set_variable(host, k, v)
