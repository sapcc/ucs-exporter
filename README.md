# ucs-exporter

Interface to access ucs metrics

## How To Run

```shell
make
python3 path/to/ucs_exporter.py -u <user> -p <password> -c <config>
```

## Collectors Information

### UcsmCollector

Information of firmware version on UCSM Server.

### UcsmChassisFaultCollector

All faults occurred on chassis.

### UcsmCRCFaultCollector

CRC faults from all the ports.

### UcsServerLicenseCollector

Port license information.
Example with values:
    License Expired : 0
    License Graceperiod : 1
    Not Applicable : 2
    License ok : 3

## Current State

Under Development
