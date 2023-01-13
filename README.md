# CiscoSwitchesConfigSaver (cisco-config-saver)

**cisco-config-saver** is a simple command-line application for saving the configuration of Cisco switches.

## Installation:

### Manual:

```
$ git clone https://github.com/vps2/cisco-config-saver
$ cd cisco-config-saver
$ python setup.py install
```

## Help:
```
$ cisco-config-save --help

CLI app for saving cisco switches configuration

options:
  -h, --help            show this help message and exit
  -b BACKUPS_DIR, --backups-dir BACKUPS_DIR
                        directory for saving devices configuration
  -a ADDRESS, --address ADDRESS
                        the ip address of the base switch that needs to be backed up
  -i INCLUDE, --include INCLUDE
                        filter the IP addresses of neighboring switches (separated by commas) for which you need to create a backup. Example:
                        [192.168.1.1,192.168.1.0/24]
  -u USER, --user USER  the name of the user to access the switches
  -p PASSWORD, --password PASSWORD
                        the user's password. If not specified, the application will ask for a password
  -s SECRET, --secret SECRET
                        password to enter the privileged mode. If not specified, the application will ask for a secret
  -d, --debug           record the output of working with devices in log files
```

## Usage examples:

### Saving the configuration of a single switch:
```
$ cisco-config-save -b ~/Downloads/backups -u user -a 192.168.1.1
```

### Saving the configuration of a single switch with saving the interaction log to a file:
```
$ cisco-config-save -b ~/Downloads/backups -u user -a 192.168.1.1 -d
```

### Saving the configuration of the base switch and all its neighbors (and their neighbors) whose IP addresses are in the subnet 192.168.1.0/24:
```
$ cisco-config-save -b ~/Downloads/backups -u user -a 192.168.1.1 -i 192.168.1.0/24
```
