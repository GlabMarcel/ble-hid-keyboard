import time
import board
import busio
import digitalio
import json
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.nordic import UARTService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
from digitalio import Direction

# Customize the device behavior here
DEVICE_NAME = "XIAO"
SHAKE_THRESHOLD = 20
DEFAULT_STRING = "Hello World"
MAX_PACKET_SIZE = 20

# Turn on IMU and wait 50 ms
imu_pwr = digitalio.DigitalInOut(board.IMU_PWR)
imu_pwr.direction = Direction.OUTPUT
imu_pwr.value = True
time.sleep(0.05)

# Initialize I2C for the IMU sensor
i2c = busio.I2C(board.IMU_SCL, board.IMU_SDA)
sensor = LSM6DS3(i2c)

# Setup BLE
ble = BLERadio()
hid = HIDService()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(hid)
advertisement.complete_name = DEVICE_NAME

# Setup HID keyboard
keyboard = Keyboard(hid.devices)

# Variable to store the string to be sent
string_to_send = DEFAULT_STRING
received_data = ""

def update_key_bindings(data):
    global string_to_send
    try:
        bindings = json.loads(data)
        for binding in bindings.get("key_bindings", []):
            if binding.get("name") == "ShakeAction":
                string_to_send = binding.get("keys", DEFAULT_STRING)
                print(f"Updated key binding: {string_to_send}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

def send_string(s):
    for char in s:
        if 'a' <= char <= 'z':
            keycode = getattr(Keycode, char.upper())
        elif 'A' <= char <= 'Z':
            keycode = getattr(Keycode, char)
        elif char == ' ':
            keycode = Keycode.SPACE
        else:
            keycode = getattr(Keycode, char, None)
        if keycode:
            keyboard.press(keycode)
            keyboard.release_all()
            time.sleep(0.1)

def is_shaken(threshold):
    accel_x, accel_y, accel_z = sensor.acceleration
    return abs(accel_x) > threshold or abs(accel_y) > threshold or abs(accel_z) > threshold

def main():
    global received_data
    print("Starting BLE...")
    while True:
        ble.start_advertising(advertisement)
        print("Advertising started")
        
        while not ble.connected:
            pass

        print("Connected")

        try:
            while ble.connected:
                if uart.in_waiting:
                    chunk = uart.read(uart.in_waiting).decode("utf-8").strip()
                    received_data += chunk
                    print(f"Received chunk: {chunk}")
                    if received_data.endswith("}"):
                        print(f"Received full data: {received_data}")
                        update_key_bindings(received_data)
                        received_data = ""  # Reset for the next set of chunks

                if is_shaken(SHAKE_THRESHOLD):
                    send_string(string_to_send)
                    time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")

        print("Disconnected")
        ble.stop_advertising()
        time.sleep(1)  # Small delay to avoid busy looping

if __name__ == "__main__":
    main()
