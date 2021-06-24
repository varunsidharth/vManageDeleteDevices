# Delete devices from vManage

This script deletes all devices in Cisco SDWAN vManage which are not registered yet (Example: Doesn't have a system IP)

## Getting Started

### Dependencies

* Python 3
* Linux / Windows / Mac OS
* requests, json, urllib3, time, getpass libraries

### vManage version tested against

* 20.5.1

## Sample output

```
[root@ranger]# python3 deleteDevices.py
vManage IP: 192.168.10.100
Username: admin
Password:

1.1.1.1 vmanage In progress
1.1.3.1 vbond   In progress
1.1.2.1 vsmart  In progress

Waiting for 3 seconds...
1.1.1.1 vmanage In progress
1.1.3.1 vbond   In progress
1.1.2.1 vsmart  In progress

Waiting for 3 seconds...
1.1.1.1 vmanage In progress
1.1.3.1 vbond   In progress
1.1.2.1 vsmart  In progress

Waiting for 3 seconds...
1.1.1.1 vmanage Success
1.1.3.1 vbond   Success
1.1.2.1 vsmart  Success

Successfully marked the Devices Invalid and syced the controllers

Deleted - ISR-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Deleted - ISR-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Deleted - CSR-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Deleted - CSR-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Deleted - C8K-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Deleted - C8K-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
Deleted - xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

[root@ranger]#
```

## Author

Varun Sidharth

## Version History

* 0.1
    * Initial Release. No major error handling