# Portable GNSS Navigation System

A MicroPython-based project that parses real-time satellite data to display navigation information on an SH1106 OLED screen. The system features a multi-page interactive interface controlled by physical buttons.

##Project Structure

 **`main.py`**: The central application logic. [cite_start]It manages UART serial communication with the GPS module, processes NMEA sentences, handles button-based navigation, and coordinates the display[cite: 1, 4].
 **`sh1106.py`**: The dedicated display driver. [cite_start]It provides the `SH1106_I2C` class, using a frame buffer to draw text and graphics to the 128x64 OLED screen via the I2C protocol[cite: 2, 3].

## Hardware Configuration

### Wiring Diagram
- [cite_start]**GPS Module (UART):** Connected via `UART 1` at 9600 baud.
  - **TX:** Pin 4
  - **RX:** Pin 5
- [cite_start]**OLED Display (I2C):** Connected via `I2C 0`.
  - **SDA:** Pin 0
  - **SCL:** Pin 1
- [cite_start]**User Buttons:** Using internal pull-up resistors.
  - [cite_start]**Button A (Pin 14):** Changes main pages and sub-pages[cite: 1, 4].
  - [cite_start]**Button B (Pin 15):** Enters and exits detailed sub-pages.

## Software Configuration

### Multi-Page User Interface
[cite_start]The system organizes information into 5 main pages, with specialized sub-pages for deeper data analysis:

1. [cite_start]**LAT/LON:** Real-time coordinates with sub-pages for Degree-Minute-Second conversion, Continent detection, and Hemisphere identification.
2. [cite_start]**Altitude:** Elevation in meters, with sub-pages for feet conversion and a percentage comparison to Mt. Everest.
3. [cite_start]**Satellites:** Active satellite count, with sub-pages for PRN IDs, constellation breakdown (GPS/Galileo/GLONASS), and a 4-bar SNR signal strength indicator.
4. [cite_start]**Time:** Displays current UTC time adjusted to a specific offset.
5. [cite_start]**Speed:** Real-time ground speed tracking in km/h.

### Advanced GPS Parsing
- [cite_start]**GGA Parsing:** Specifically extracts altitude and the number of satellites used for the current fix.
- [cite_start]**RMC Parsing:** Retrieves Latitude, Longitude, ground speed (knots converted to km/h), and UTC time.
- [cite_start]**GSV Parsing:** Identifies individual satellites in view, their PRN IDs, and Signal-to-Noise Ratio (SNR) for signal quality monitoring.

### Display Performance (`sh1106.py`)
- [cite_start]**FrameBuffer Support:** Inherits from MicroPython's `framebuf` for efficient drawing[cite: 2].
- [cite_start]**Optimized Refresh:** The `show()` method updates the physical display page by page to ensure smooth performance on low-power microcontrollers[cite: 3].

## Getting Started
1. Install MicroPython on your microcontroller (e.g., Raspberry Pi Pico).
2. Upload `sh1106.py` to your board's root directory.
3. Upload `main.py` and run it to initialize the system.
4. Ensure your GPS module has a clear view of the sky to acquire a "Fix."

