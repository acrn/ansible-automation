#!/usr/bin/python3

import collections
import itertools
import json
import sys

reversed_inventory = {
    'dependencies': {
        'devmachine':   ['workstation'],
        'chromebook':   ['workstation']},
    'groups_by_host': {
        'atom':         ['systemd_networkd', 'dnsserver', 'dhcpserver'],
        'bismuth':      ['devmachine'],
        'carbon':       ['systemd_networkd',
                         'devmachine',
                         'dnsserver',
                         'mount_nfs'],
        'cerium':       ['devmachine'],
        'chrome':       ['chromebook', 'workstation'],
        'dhcp1':        ['dhcpserver'],
        'dhcp2':        ['dhcpserver'],
        'ns1':          ['dnsserver'],
        'ns2':          ['dnsserver'],
        'git':          ['gitserver'],
        'helium':       ['systemd_networkd', 'raspberrypi', 'webserver'],
        'media':        ['mediaserver'],
        'pxe':          ['pxeserver'],
        'sodium':       ['devmachine']},
    'host_vars': {}}

def expand_dependencies(groups_by_host, dependencies):

    def expand_dependency(group):
        for x in dependencies.get(group, ''):
            yield from expand_dependency(x)
        yield group

    for host, groups in groups_by_host:
        expanded_groups = itertools.chain.from_iterable(
                            expand_dependency(group) for group in groups)
        yield (host, expanded_groups)

def reverse_groups_by_host(groups_by_host):
    out = collections.defaultdict(lambda: {'hosts': [], 'vars': {}})
    for host, groups in groups_by_host:
        for group in groups:
            out[group]['hosts'].append(host)
    return out

def inject_meta(inventory, host_vars):
    meta = inventory['_meta'] = {}
    hostvars = meta['hostvars'] = {}
    for host, vars_ in host_vars.items():
        hostvars[host] = vars_

def main():

    groups_by_host = reversed_inventory['groups_by_host'].items()
    dependencies = reversed_inventory['dependencies']
    host_vars = reversed_inventory['host_vars']

    expanded_groups_by_hosts = expand_dependencies(groups_by_host, dependencies)
    unreversed_inventory = reverse_groups_by_host(expanded_groups_by_hosts)
    inject_meta(unreversed_inventory, host_vars)

    if '--test' in sys.argv:
        pass
    elif '--list' in sys.argv or '--host' in sys.argv:
        print(json.dumps(unreversed_inventory))
