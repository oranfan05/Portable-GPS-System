from machine import UART, Pin, I2C
import sh1106
import time

#====================================
# GPS + OLED GNSS Display System
#===================================

# ---------------- Hardware Settings ----------------


# Connecting UART(Universal Asynchronous Receiver Transmitter) to GPS module
# TX = Transmitter = Pin 4
# RX = Receiver = Pin 5

uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))


# I2C OLED display as 128 x 64
# I2C = Inter-intergrated Circuit
# SDA = Serial Data --> Pin 0
# SCL = Serial Clock --> Pin 1

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = sh1106.SH1106_I2C(128, 64, i2c)

# Blue buttons = Pin 14
# Red buttons = Pin 15
# Set the button's initial value as 1

btn_a = Pin(14, Pin.IN, Pin.PULL_UP)
btn_b = Pin(15, Pin.IN, Pin.PULL_UP)

last_a = 1
last_b = 1

# ---------------- Software Setup  ----------------

# Pages control
page = 1
subpage = 1
in_subpage = False

buffer = ""

# GPS Data Storage
lat = None
lon = None
ns = ""
ew = ""

sats = 0
alt = 0.0
speed = 0.0
time_str = ""
last_time = ""

# Satellite Details
sat_prn = []  # List of Satellite PRN numbers
sat_sys = []  # List of constellation names (eg: GPS, GLONASS, etc)
sat_snr = []  # Signal strength values

# ---------------- GPS Helpers Functions ----------------
def convert_to_decimal(raw, direction):

    """
    Convert NMEA (National Marine Electronics Association) coordinate formate
    to standard decimal degrees
    
    eg: 492N -> 49.3
    
    """
    
    # If GPS has no fix, coordinate field may be empty
    if raw == "":
        return None
        
    # Extract degrees
    deg = int(float(raw) / 100)
    
    # minutes
    minutes = float(raw) - (deg * 100)
    
    # Minutes to degrees
    decimal = deg + (minutes / 60)
    
    # Apply negative sign for South or West hemisperes
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

# Main Program Loop

last_frame = time.ticks_ms()

while True:

    # Check if GPS has sent any data
    if uart.any():
        data = uart.read()
        if data:
            try:
                
                # Append new data to buffer
                buffer += data.decode()

                # Process compete NMEA sentences which end with newline
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    # GGA = Global Positioning System Fix Data
                    # It contains satellite count and altitude
                    # Satellite is recorded in part 7
                    # Altitude is recorded in part 9
                    if line.startswith("$GNGGA") or line.startswith("$GPGGA"):
                        parts = line.split(",")
                        if len(parts) > 9:
                            sats = int(parts[7]) if parts[7] else 0
                            alt = float(parts[9]) if parts[9] else 0.0

                    # RMC = recommended minimum data
                    # It contains latitude and longitude, speed, UTC time
                    # From the parts finding the values of the latitude and longitude, speed, UTC time
                    if line.startswith("$GNRMC") or line.startswith("$GPRMC"):
                        parts = line.split(",")

                        if len(parts) > 6:

                            if parts[2] == "A":
                                lat = convert_to_decimal(parts[3], parts[4])
                                lon = convert_to_decimal(parts[5], parts[6])

                                ns = parts[4]
                                ew = parts[6]

                            if parts[7]:
                                speed = float(parts[7]) * 1.852

                            if parts[1]:
                                raw = parts[1]
                                h = int(raw[0:2]) - 4
                                if h < 0:
                                    h += 24
                                m = int(raw[2:4])
                                s = int(raw[4:6])
                                time_str = f"{h:02}:{m:02}:{s:02}"

                    # GSA = Satellite info
                    # Contains satellite PRN numbers, elevation, azimuth, signal strength
                    if line.startswith("$GNGSA") or line.startswith("$GPGSA"):
                        parts = line.split(",")
                        # This gives PRN numbers but not constellation names easily
                        pass

                    # GSV = Satellites in view
                    if line.startswith("$GNGSV") or line.startswith("$GPGSV"):
                        parts = line.split(",")
                        # Analyse satellite data
                        # For a real implementation, you will analyse all GSV sentences
                        if len(parts) >= 8:
                            # Clear lists periodically
                            if len(sat_prn) > 20:
                                sat_prn.clear()
                                sat_sys.clear()
                                sat_snr.clear()
                            
                            # Analyse up to 4 satellites per GSV sentence
                            for i in range(4):
                                idx = 4 + (i * 4)
                                if idx + 2 < len(parts):
                                    try:
                                        prn = int(parts[idx]) if parts[idx] else 0
                                        snr = int(parts[idx+2]) if parts[idx+2] else 0
                                        
                                        if prn > 0:
                                            sat_prn.append(prn)
                                            sat_snr.append(snr)
                                            
                                            # Determine constellation based on PRN range
                                            if 1 <= prn <= 32:
                                                sat_sys.append("GPS")
                                            elif 65 <= prn <= 96:
                                                sat_sys.append("GLONASS")
                                            elif 193 <= prn <= 202:
                                                sat_sys.append("Galileo")
                                            else:
                                                sat_sys.append("GNSS")
                                    except(ValueError, IndexError):
                                        pass

            except(UnicodeDecodeError):
                pass

# ---------------- Controls ----------------
    # Button controls
    a = btn_a.value()
    b = btn_b.value()

    if last_a == 1 and a == 0:
        if not in_subpage:
            page += 1
            # By pressing the button it will move to next page
            if page > 5:
                page = 1
        else:
            subpage += 1
            if subpage > 3:
                subpage = 1
            
    # Once button pressed, it will enter / exit the subpage
    if last_b == 1 and b == 0:
        if not in_subpage:
            in_subpage = True
            subpage = 1
        else:
            in_subpage = False

    last_a = a
    last_b = b

# ---------------- Display ----------------
    now = time.ticks_ms()
    if time.ticks_diff(now, last_frame) >= 16:
        last_frame = now

        oled.fill(0)

        # Titles
        oled.text("GNSS", 0, 0)

        if not in_subpage:
            oled.text("P:" + str(page), 80, 0)
        else:
            oled.text("P:" + str(page) + chr(64 + subpage), 60, 0)

        # Main page 
        if not in_subpage:

            if page == 1:
                oled.text("LAT/LON", 0, 20)

                if lat:
                    oled.text(str(lat) + " " + ns, 0, 35)
                else:
                    oled.text("Lat: No Fix", 0, 35)

                if lon:
                    oled.text(str(lon) + " " + ew, 0, 50)
                else:
                    oled.text("Lon: No Fix", 0, 50)

            elif page == 2:
                oled.text("Altitude:", 0, 30)
                oled.text(str(int(alt)) + " m", 0, 45)

            elif page == 3:
                oled.text("Satellites:", 0, 30)
                oled.text(str(sats), 0, 45)

            elif page == 4:
                oled.text("TIME", 0, 30)
                oled.text(time_str, 0, 45)

            elif page == 5:
                oled.text("SPEED", 0, 30)
                oled.text(str(int(speed)) + " km/h", 0, 45)

        # Subpage
        else:

            if page == 1:

                if subpage == 1:
                    oled.text("Minutes:", 0, 10)

                    if lat and lon:
                        lat_d = int(lat)
                        lat_m = int(abs(lat - lat_d) * 60)
                        lat_s = int((((abs(lat - lat_d) * 60) - lat_m) * 60))

                        oled.text("LAT:", 0, 20)
                        oled.text(f"{lat_d} {lat_m}' {lat_s}\"", 0, 30)

                        lon_d = int(lon)
                        lon_m = int(abs(lon - lon_d) * 60)
                        lon_s = int((((abs(lon - lon_d) * 60) - lon_m) * 60))

                        oled.text("LON:", 0, 45)
                        oled.text(f"{lon_d} {lon_m}' {lon_s}\"", 0, 55)

                    else:
                        oled.text("No Fix", 0, 40)

                elif subpage == 2:
                    oled.text("Continent:", 0, 10)

                    if lat and lon:

                        if lat > 15 and lon < -30:
                            cont = "N America"
                        elif lat < 15 and lat > -60 and lon < -30:
                            cont = "S America"
                        elif lat > 35 and -30 < lon < 60:
                            cont = "Europe"
                        elif lat > 0 and lon >= 60:
                            cont = "Asia"
                        elif lat < 35 and lat > -35 and -20 < lon < 55:
                            cont = "Africa"
                        elif lat < -10 and lon > 110:
                            cont = "Australia"
                        elif lat < -60:
                            cont = "Antarctica"
                        else:
                            cont = "Ocean"

                        oled.text(cont, 0, 40)

                    else:
                        oled.text("No Fix", 0, 40)

                elif subpage == 3:
                    oled.text("Hemisphere:", 0, 10)

                    if lat is not None and lon is not None:

                        if lat > 0:
                            lat_hemi = "North Hemisphere"
                        else:
                            lat_hemi = "South Hemisphere"

                        if lon > 0:
                            lon_hemi = "East Hemisphere"
                        else:
                            lon_hemi = "West Hemisphere"

                        oled.text("LAT:", 0, 20)
                        oled.text(lat_hemi, 0, 30)

                        oled.text("LON:", 0, 45)
                        oled.text(lon_hemi, 0, 55)

                    else:
                        oled.text("No Fix", 0, 35)

            # Subpage for page 2
            elif page == 2:

                # 2A → Feet
                if subpage == 1:
                    oled.text("American:", 0, 30)

                    if alt is not None:
                        alt_ft = alt * 3.28084
                        oled.text(str(int(alt_ft)) + " ft", 0, 45)
                    else:
                        oled.text("No Data", 0, 35)

                # 2B → % Everest
                elif subpage == 2:
                    oled.text("% to Everest", 0, 10)

                    EVEREST = 8848  # meters

                    if alt is not None:
                        percent = (alt / EVEREST) * 100
                        oled.text(f"{percent:.2f}%", 0, 35)
                    else:
                        oled.text("No Data", 0, 35)

                # 2C → raw number display
                elif subpage == 3:
                   
                    oled.text("3306410", 0, 35)

            # Page 3
            elif page == 3:

                # 3A → PRN IDs
                if subpage == 1:
                    oled.text("PRN IDs", 0, 10)

                    if sat_prn:
                        # Show first 6 PRN numbers
                        prn_str = " ".join(str(p) for p in sat_prn[:6])
                        oled.text(prn_str, 0, 35)
                    else:
                        oled.text("No Data", 0, 35)

                # 3B → Constellation
                elif subpage == 2:
                    oled.text("Constellation", 0, 10)

                    if sat_sys:
                        # Count constellation types
                        gps = sat_sys.count("GPS")
                        gal = sat_sys.count("Galileo")
                        glo = sat_sys.count("GLONASS")

                        if gps >= gal and gps >= glo:
                            c = "GPS"
                        elif gal >= gps and gal >= glo:
                            c = "Galileo"
                        else:
                            c = "GLONASS"

                        oled.text(c, 0, 35)
                        oled.text(f"({gps}/{gal}/{glo})", 0, 50)
                    else:
                        oled.text("No Signal", 0, 35)

                # 3C → Signal Bars
                elif subpage == 3:
                    oled.text("Signal Bars", 0, 10)

                    if sat_snr:
                        avg = sum(sat_snr) / len(sat_snr)

                        # convert to 0–4 bars
                        if avg < 10:
                            bars = 0
                        elif avg < 20:
                            bars = 1
                        elif avg < 30:
                            bars = 2
                        elif avg < 40:
                            bars = 3
                        else:
                            bars = 4

                        oled.text(f"Avg SNR: {int(avg)}", 0, 25)
                        oled.text("█" * bars + "░" * (4 - bars), 0, 45)
                    else:
                        oled.text("No Signal", 0, 35)

        oled.show()
