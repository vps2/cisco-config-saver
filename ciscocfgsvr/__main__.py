import argparse
import getpass
import os
import pathlib
import re
import time
from collections import deque

from netmiko import BaseConnection, ConnectHandler, NetmikoTimeoutException

from ciscocfgsvr.writeable_dir import WriteableDir
from ciscocfgsvr.valid_network_or_ip import ValidNetworkOrIP
from ciscocfgsvr.ip_filter import IPFilter


class _OpenFileError(Exception):
    pass


def _create_args_parser():
    parser = argparse.ArgumentParser(description="CLI app for saving cisco switches configuration")
    parser.add_argument('-b',
                        '--backups-dir',
                        type=pathlib.Path,
                        required=True,
                        action=WriteableDir,
                        help="directory for saving devices configuration")
    parser.add_argument('-a',
                        '--address', 
                        type=str, 
                        required=True,
                        action=ValidNetworkOrIP, 
                        help='the ip address of the base switch that needs to be backed up')
    parser.add_argument('-i',
                        '--include',
                        type=str,
                        action=ValidNetworkOrIP,
                        help='filter the IP addresses of neighboring switches (separated by commas) for which you need to create a backup. Example: [192.168.1.1,192.168.1.0/24]')
    parser.add_argument('-u',
                        '--user',
                        type=str,
                        required=True,
                        help='the name of the user to access the switches')
    parser.add_argument('-p',
                        '--password',
                        type=str,
                        help="the user's password. If not specified, the application will ask for a password")
    parser.add_argument('-s',
                        '--secret',
                        type=str,
                        help="password to enter the privileged mode. If not specified, the application will ask for a secret")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help="record the output of working with devices in log files")
    
    return parser


def _open_file(name, mode='r', bufsize=-1, encoding=None, errors=None):
    try:
        return open(name, mode, bufsize, encoding, errors)
    except OSError as e:
        args = {'filename': name, 'error': e}
        message = "can't open '%(filename)s': %(error)s"
        raise _OpenFileError(message % args) from e

def _connect_to_cisco(**device) -> BaseConnection:
    conn = None

    device['device_type'] = 'cisco_ios_telnet'

    try:
       conn = ConnectHandler(**device)
    except ConnectionRefusedError:
        device["device_type"] = 'cisco_ios'
        conn = ConnectHandler(**device)

    return conn

def _exec_show_command(conn: BaseConnection, cmd: str) -> str:
    prompt = conn.find_prompt()
    
    more_string = "--More--"

    output: str = conn.send_command(cmd, expect_string=f'{more_string}|{prompt}')

    #этот блок нужен, если команды 'terminal width 511' и 'terminal length 0' не разрешены. Данные команды запускаются внутри самой библиотеки
    if conn.find_prompt().endswith(more_string):
        output = output[:-(len(more_string) + 2)]  # убираем --More--\s из первого вывода
        conn.write_channel(" ")
        while True:
            try:
                page = conn.read_channel()

                output += re.sub(r'\s?\b{9}\s{8}\b{9}', '', page)  # почему то в начале вывода появляются какие-то непечатаемые символы

                if more_string in page:
                    output = output[:-(len(more_string) + 2)]  # убираем --More-- из остальных выводов
                    conn.write_channel(" ")
                elif prompt in output:
                    break
            except NetmikoTimeoutException:
                break

    return output


def _make_backup(conn: BaseConnection, backups_path: str):
    conn.enable()

    hostname = conn.find_prompt()
    hostname = hostname[:-1] or "unknown"

    show_run_output = _exec_show_command(conn, 'sh run')
    show_vlan_output = _exec_show_command(conn, 'sh vlan')
    show_ver_output = _exec_show_command(conn, 'sh ver')

    conn.exit_enable_mode()

    outfile_name = "".join([hostname, '_', time.strftime("%Y%m%d-%H%M%S"), '.conf'])
    outfile_path = os.path.join(backups_path, outfile_name)
    with _open_file(outfile_path, 'w') as file:
        file.write('--> show running-configuration:\n\n')
        file.write(show_run_output)
        file.write('\n\n\n--> show vlan:\n')
        file.write(show_vlan_output)
        file.write('\n\n\n--> show version:\n\n')
        file.write(show_ver_output)


def _get_neighbors(conn: BaseConnection):
    output = _exec_show_command(conn, 'sh cdp nei det')
    
    pattern = re.compile(r'Device ID: (.*?)\n.*?\n.*?IP address: (.*?)\n')
    device_separator = '-------------------------'
    devices = []
    for rawData in output.split(device_separator):
        m :re.Match = pattern.search(rawData)
        if(m):
            devices.append(m.groups())
    
    return devices


def main():
    try:
        try:
            args_parser = _create_args_parser()
            args = vars(args_parser.parse_args())
        except Exception as error:
            print(error)
            os._exit(1)

        device_ip = args['address']
        login = args['user']
        password = getpass.getpass("Password: ") if args['password'] == None else args['password']
        secret = getpass.getpass("Secret: ") if args['secret'] == None else args['secret']

        backups_path = args['backups_dir']

        ip_filter = None
        include = args['include']
        if include:
            ip_filter = IPFilter(include.split(','))

        ##############################################################################################3

        devices = deque()
        devices.append(device_ip)
        visited_devices = []
        while True:
            if len(devices) == 0:
                break

            device_ip = devices.pop()
            if device_ip in visited_devices:
                continue

            visited_devices.append(device_ip)

            device = {
                'host': device_ip,
                'username': login,
                'password': password,
                'secret': secret,
                'global_delay_factor': 1.3,  # чтобы не пропустить долго формируемый вывод
            }
            if args['debug']:
                device['session_log'] = f"output_{device_ip}.txt"

            print('Working with:', device_ip)

            try:
                with _connect_to_cisco(**device) as conn:
                    _make_backup(conn, backups_path)
                    if ip_filter:
                        neighbors = _get_neighbors(conn)
                        for neighbor in neighbors:
                            ip = neighbor[1]
                            if ip_filter.is_allow(ip):
                                devices.append(ip)
            except Exception as error:
                print(f'error: {error}: {device_ip}')  
    except KeyboardInterrupt:
        pass        


if __name__ == "__main__":
    main()
