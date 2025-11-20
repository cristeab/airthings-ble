# airthings-ble

Sample Python script to interact with Airthings devices using
[airthings-ble](https://github.com/Airthings/airthings-ble/tree/main) library.

Usage examples:

- scan for all BLE devices and print Airthings devices information if any:

    ./scan_airthings_devices.py --timeout 10

- read the BLE device information given by its MAC address:

    ./scan_airthings_devices.py --timeout 10 --connect \<MAC address\>
