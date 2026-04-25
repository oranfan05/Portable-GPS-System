“”Portable GNSS Navigation System””

A MicroPython-based project that parses real-time satellite data to display navigation information on an SH1106 OLED screen. The system provides a multi-page interactive interface for geospatial tracking.

“Hardware Setup Instructions”

The system is built on a MicroPython-compatible microcontroller (such as a Raspberry Pi Pico) using the following pinout:

GNSS Module (UART):
Uses UART 1 at 9600 baud.

TX: Pin 4

RX: Pin 5

OLED Display (I2C): Uses I2C 0 at address 0x3C.

SDA: Pin 0     SCL: Pin 1

User Interface Buttons: 
Configured with internal pull-up resistors.

Button A (Main Navigation): Pin 14, Blue Button 

Button B (Sub-page Navigation): Pin 15, Red Button 




“Dependencies and Libraries”

The project requires the following files and libraries to be present on the microcontroller:

Standard Libraries: machine, time, and framebuf (these are built-in to MicroPython firmware).
“sh1106.py”: The dedicated hardware driver for the 128x64 OLED screen.
‘main.py”: The application logic and GPS parsing script.


“Build and Run Instructions”

1. Prepare Hardware: Wire the components according to the Hardware Setup section above.
2. Flash Firmware: Ensure your board has the latest MicroPython firmware installed.
3. Upload Files: Use an IDE like Thonny to upload both "sh1106.py" and "main.py" to the root directory of your device.
4. Execute: Run “main.py”. The display will initialize with a "GNSS" header.
5. Acquire Fix: Ensure the GPS module has a clear view of the sky to begin receiving data.


“How to Use”

Once the system is running, you can interact with the data using the hardware buttons:


Button Control: 

Button A (blue): Use this to cycle through the 5 Main Pages (Lat/Lon, Altitude, Satellites, Time, Speed).

Button B (red): Use this to Enter or Exit sub-pages for more detailed data.

Display Pages:
1. Latitude/Longitude: Shows decimal coordinates. Sub-pages include DMS (Degrees, Minutes, Seconds) and Continent detection.
2. Altitude: Displays elevation in meters. Sub-pages show conversion to feet and a height comparison to Mt. Everest.
3. Satellites: Shows total satellites in use. Sub-pages list PRN IDs, identify constellations (GPS/Galileo/GLONASS), and show Signal Strength bars.
4. Time: Displays current UTC time adjusted for local offset.
5. Speed: Displays real-time ground speed in km/h.



“Technical Features”

Message Format: Processes NMEA 0183 standard sentences (GGA, RMC, and GSV).

Timing & Sync: The UI refreshes every 16ms (~60 FPS) using non-blocking time.ticks_ms logic.

Error Handling: Includes robust protection against serial noise (UnicodeDecodeError) and malformed data packets (ValueError, IndexError) to ensure the system does not crash during signal loss.
