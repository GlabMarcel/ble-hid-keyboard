
# BLE HID Keyboard Project

This project implements a BLE HID keyboard with configurable key bindings that can be updated via a GUI application.

## Structure

- `firmware/`: Firmware code for the microcontroller.
- `host/`: Host application code for configuring the keyboard.
- `docs/`: Project documentation.
- `tests/`: Test scripts for validating the project.

## Setup

### Firmware

1. Copy the contents of the `firmware/` directory to your microcontroller.
2. Ensure you have the necessary libraries in the `lib/` directory.

### Host Application

1. Navigate to the `host/` directory.
2. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the host application:
   ```sh
   python nrf_ui.py
   ```

## Usage

1. Power on your microcontroller and ensure it is advertising.
2. Use the host application to configure key bindings.
3. Shake the microcontroller to send the configured key bindings as keystrokes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
