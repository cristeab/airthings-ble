#!/usr/bin/env python3
"""
Example: read data from Airthings Corentium Home 2 using the
`airthings_ble` package (which wraps bleak and decoding logic).

Usage:
  - List discovered devices:
      python scan_airthings_devices.py --timeout 8

  - Connect to a device and print its sensors:
      python scan_airthings_devices.py --connect AA:BB:CC:DD:EE:FF
"""
from __future__ import annotations

import argparse
import asyncio
import logging
from typing import Optional

from bleak import BleakScanner

from airthings_ble import AirthingsBluetoothDeviceData, UnsupportedDeviceError


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Read Airthings Corentium Home 2 data")
    p.add_argument("--connect", "-c", help="Bluetooth address to connect to (optional)")
    p.add_argument("--timeout", "-t", type=float, default=8.0, help="Scan timeout in seconds")
    p.add_argument("--imperial", action="store_true", help="Show non-metric units when applicable")
    p.add_argument("--debug", action="store_true", help="Enable debug logging")
    return p.parse_args()


async def scan(timeout: float):
    print(f"Scanning for BLE devices for {timeout} seconds...")
    devices = await BleakScanner.discover(timeout=timeout)
    if not devices:
        print("No BLE devices found")
        return []

    print(f"Found {len(devices)} device(s)")
    return devices


def print_device(device) -> None:
    print("Device info:")
    print(f"  Name: {device.name}")
    print(f"  Model: {device.model.product_name if device.model else device.model}")
    print(f"  Manufacturer: {device.manufacturer}")
    print(f"  Serial: {device.identifier}")
    print(f"  Firmware: {device.sw_version}")
    print(f"  Address: {device.address}")
    print("Sensors:")
    for k, v in sorted(device.sensors.items()):
        print(f"  {k}: {v}")
    print("\n")


async def connect_and_read(address: str, timeout: float, is_metric: bool) -> None:
    devices = await BleakScanner.discover(timeout=timeout)
    target = None
    for d in devices:
        if d.address.lower() == address.lower():
            target = d
            break
    if target is None:
        print(f"Device with address {address} not found during scan.")
        print("Run without --connect to list available addresses.")
        return

    logger = logging.getLogger("airthings_ble_example")
    client = AirthingsBluetoothDeviceData(logger=logger, is_metric=is_metric)

    try:
        print(f"Connecting to {target.address} ...")
        device = await client.update_device(target)
        print_device(device)
    except UnsupportedDeviceError:
        logger.error("The device is not a supported Airthings device.")
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(f"Error connecting/reading device: {exc}")


async def auto_find_and_read(timeout: float, is_metric: bool) -> None:
    devices = await BleakScanner.discover(timeout=timeout)
    if not devices:
        print("No BLE devices found")
        return

    logger = logging.getLogger("airthings_ble_example")
    client = AirthingsBluetoothDeviceData(logger=logger, is_metric=is_metric)

    for d in devices:
        try:
            print(f"Attempting to read {d.address} ({d.name})")
            device = await client.update_device(d)
            print_device(device)
        except UnsupportedDeviceError:
            logger.error(f"Unsupported Airthings device at {d.address}")
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f"Error reading {d.address}: {exc}")


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.connect:
        asyncio.run(connect_and_read(args.connect, args.timeout, not args.imperial))
    else:
        # Default: list and try to auto-detect Airthings devices
        asyncio.run(scan(args.timeout))
        asyncio.run(auto_find_and_read(args.timeout, not args.imperial))


if __name__ == "__main__":
    main()
