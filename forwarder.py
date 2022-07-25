#!/usr/bin/env python3

from time import sleep
from subprocess import check_output, check_call, CalledProcessError
from typing import List, Dict
from json import loads, JSONDecodeError


def strip_output(output: List[str]) -> List[str]:
    return [line.rstrip() for line in output]


def inspect_container(container: str) -> List[int]:
    # print(f'Inspecting container {container} ...')
    try:
        info = loads(check_output(['docker', 'inspect', container]).decode())
        external_ports = info[0]['NetworkSettings']['Ports']
        ports_to_publish = set()
        for internal_port, external_ports in external_ports.items():
            if not internal_port.endswith('/tcp'):
                continue  # We forward only TCP connections.
            for port in external_ports:
                if port['HostIp'] in ('0.0.0.0', '::'):
                    ports_to_publish.add(int(port['HostPort']))
        return sorted(ports_to_publish)
    except (CalledProcessError, JSONDecodeError) as e:
        print(f'Could not inspect container {container}, error: {str(e)}.')
        return []


def inspect_virtual_machine() -> Dict[int, List[str]]:
    info = strip_output(check_output(['vboxmanage', 'showvminfo', 'docker-service', '--machinereadable']).decode().rstrip().split('\n'))
    forwarded_ports = {}
    for port in [line for line in info if line.startswith('Forwarding(')]:
        name, protocol, host_ip, host_port, guest_ip, guest_port = port.split('=')[1][1:-1].split(',')
        host_port, guest_port = int(host_port), int(guest_port)
        if name == 'ssh':
            continue  # Do not ever touch SSH.
        if protocol != 'tcp':
            continue  # We forward only TCP connections.
        if guest_port == 2375:
            continue  # Do not touch Docker.
        if guest_port not in forwarded_ports:
            forwarded_ports[guest_port] = []
        forwarded_ports[guest_port].append(name)
    return forwarded_ports


def delete_rule(port: int, rules_to_remove: List[str]) -> None:
    try:
        for rule in rules_to_remove:
            check_call(['vboxmanage', 'controlvm', 'docker-service', 'natpf1', 'delete', rule])
    except CalledProcessError as e:
        print(f'Could not delete rule for port {port}, error: {str(e)}.')


def add_rule(port: int) -> None:
    try:
        check_call(['vboxmanage', 'controlvm', 'docker-service', 'natpf1', f',tcp,127.0.0.1,{port},,{port}'])
    except CalledProcessError as e:
        print(f'Could not add rule for port {port}, error: {str(e)}.')


def iterate():
    # print('Enumerating running containers ...')
    try:
        containers = strip_output(check_output(['docker', 'ps', '--no-trunc', '-q']).decode().rstrip().split('\n'))
    except CalledProcessError as e:
        print(f'Could not enumerate containers, error: {str(e)}.')
        return
    containers = [line.rstrip() for line in containers if len(line.rstrip()) > 0]
    if not containers:
        # print('No running containers have been detected.')
        return
    # print(f'{len(containers)} running container(s) has/have been detected.')

    # print('Inspecting containers ...')
    ports_to_publish = []
    for container in containers:
        ports_to_publish.extend(inspect_container(container))
    # print(f'Ports requiring publishing: {", ".join([str(port) for port in ports_to_publish])}.')

    # print('Inspecting VM ...')
    forwarded_ports = inspect_virtual_machine()
    # print(f'Already forwarded ports: {", ".join([str(port) for port in sorted(forwarded_ports.keys())])}')

    excessive_ports = sorted(set(forwarded_ports.keys()) - set(ports_to_publish))
    for port in excessive_ports:
        print(f'Deleting rule for port {port} ...')
        delete_rule(port, forwarded_ports[port])

    missing_ports = sorted(set(ports_to_publish) - set(forwarded_ports.keys()))
    for port in missing_ports:
        print(f'Adding rule for port {port} ...')
        add_rule(port)


def main():
    while True:
        iterate()
        sleep(1)


if __name__ == '__main__':
    main()
