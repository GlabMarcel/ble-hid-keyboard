import json
import asyncio
import threading
import tkinter as tk
from tkinter import messagebox
from bleak import BleakClient, BleakError
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

DEVICE_NAME = "XIAO"
DEVICE_ADDRESS = "C9:3A:11:6F:7C:43"
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
TX_CHARACTERISTIC_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
RX_CHARACTERISTIC_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
MAX_PACKET_SIZE = 20

class KeyBindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Binding Configuration")

        self.label = tk.Label(root, text="Enter the key binding (e.g., 'Hello World'):")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=10)

        self.save_button = tk.Button(root, text="Save and Send", command=self.save_and_send_binding)
        self.save_button.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Ready")
        self.status_label.pack(pady=10)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.ble_client = BleakClient(DEVICE_ADDRESS)

        threading.Thread(target=self.run_event_loop).start()

    def run_event_loop(self):
        logging.debug("Starting event loop")
        try:
            self.loop.run_forever()
        except Exception as e:
            logging.error(f"Exception in event loop: {e}")
            logging.exception("Exception occurred in event loop")

    async def connect_to_device(self):
        logging.debug("Attempting to connect to BLE device...")
        try:
            await self.ble_client.connect()
            if self.ble_client.is_connected:
                self.status_label.config(text="Status: Connected")
                logging.debug("Connected to BLE device")
                # Log available services and characteristics
                services = await self.ble_client.get_services()
                for service in services:
                    logging.debug(f"Service: {service.uuid}")
                    for char in service.characteristics:
                        logging.debug(f"  Characteristic: {char.uuid}, Properties: {char.properties}")
            else:
                self.status_label.config(text="Status: Failed to connect")
                logging.debug("Failed to connect to BLE device")
        except BleakError as e:
            self.status_label.config(text=f"Status: Connection error {str(e)}")
            logging.error(f"Connection error: {str(e)}")
        except Exception as e:
            self.status_label.config(text=f"Status: Unexpected error {str(e)}")
            logging.error(f"Unexpected error: {str(e)}")
            logging.exception("Exception occurred during connection")

    def save_and_send_binding(self):
        logging.debug("save_and_send_binding called")
        key_binding = self.entry.get()
        try:
            data = {"key_bindings": [{"name": "ShakeAction", "keys": key_binding}]}
            json_data = json.dumps(data)
            logging.debug(f"Prepared data to send: {json_data}")
            future = asyncio.run_coroutine_threadsafe(self._send_binding_async(json_data), self.loop)
            future.add_done_callback(self._on_send_complete)
        except Exception as e:
            self.status_label.config(text=f"Status: Failed to save key binding ({e})")
            messagebox.showerror("Error", f"Failed to save key binding: {e}")

    def _on_send_complete(self, future):
        logging.debug("Entering _on_send_complete")
        try:
            result = future.result()
            logging.debug(f"Send operation completed with result: {result}")
        except Exception as e:
            logging.error(f"Send operation failed with exception: {e}")
            messagebox.showerror("Error", f"Failed to send key binding: {e}")

    async def _send_binding_async(self, data):
        logging.debug("Entering _send_binding_async")
        try:
            if not self.ble_client.is_connected:
                logging.debug("Client is not connected, attempting to reconnect...")
                await self.connect_to_device()

            if self.ble_client.is_connected:
                logging.debug("Sending data to BLE device...")
                for i in range(0, len(data), MAX_PACKET_SIZE):
                    chunk = data[i:i + MAX_PACKET_SIZE]
                    logging.debug(f"Sending chunk: {chunk}")
                    try:
                        await self.ble_client.write_gatt_char(RX_CHARACTERISTIC_UUID, chunk.encode('utf-8'))
                        logging.debug(f"Successfully sent chunk: {chunk}")
                    except Exception as e:
                        logging.error(f"Failed to send chunk: {chunk}. Error: {str(e)}")
                        raise e
                    await asyncio.sleep(0.05)  # Small delay to ensure chunks are processed in order
                self.status_label.config(text=f"Status: Sent binding '{data}'")
                logging.debug(f"Sent binding '{data}' to BLE device")
            else:
                self.status_label.config(text="Status: Failed to reconnect")
                logging.debug("Failed to reconnect to BLE device")
        except Exception as e:
            self.status_label.config(text=f"Status: Failed to send {str(e)}")
            logging.error(f"Failed to send binding '{data}' to BLE device: {str(e)}")
            logging.exception("Exception occurred during sending binding")

def run_gui():
    root = tk.Tk()
    app = KeyBindingApp(root)
    root.mainloop()

if __name__ == "__main__":
    logging.debug("Starting GUI")
    run_gui()
