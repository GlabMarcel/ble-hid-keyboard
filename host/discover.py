import asyncio
from bleak import BleakScanner, BleakClient # type: ignore

DEVICE_NAME = "XIAO"

async def discover_services(device_name):
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == device_name:
            async with BleakClient(device) as client:
                print(f"Connected to {device.name} ({device.address})")
                services = await client.get_services()
                for service in services:
                    print(f"Service: {service.uuid}")
                    for characteristic in service.characteristics:
                        print(f"  Characteristic: {characteristic.uuid}, Properties: {characteristic.properties}")
                return

asyncio.run(discover_services(DEVICE_NAME))
