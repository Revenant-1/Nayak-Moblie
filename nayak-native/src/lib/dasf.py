import serial
import time


# =====================================================
# SETTINGS
# =====================================================

PORT = "/dev/cu.usbserial-0001"
BAUD = 921600


# =====================================================
# SCHEMES
# =====================================================
#
# Add/edit your schemes here.
#
# "title"  = first line
# "line1"  = second line
# "line2"  = third line
#
# Keep the text short enough for the 128x64 OLED.
#

SCHEMES = [

    # -------------------------------------------------
    # 1. PM KISAN
    # -------------------------------------------------

    {
        "title": "PM KISAN",

        "full_name":
            "Pradhan Mantri Kisan Samman Nidhi",

        "purpose":
            "Income support for eligible landholding farmer families",

        "benefit":
            "Rs 6000 per year",

        "payment":
            "3 installments of Rs 2000 each",

        "eligibility":
            "Eligible landholding farmer families",

        "method":
            "Direct Benefit Transfer",

        "line1":
            "Rs 6000 per year",

        "line2":
            "3 installments"
    },


    # -------------------------------------------------
    # 2. AYUSHMAN BHARAT
    # -------------------------------------------------

    {
        "title": "AYUSHMAN",

        "full_name":
            "Ayushman Bharat PM-JAY",

        "purpose":
            "Health protection for eligible beneficiaries",

        "benefit":
            "Up to Rs 5 lakh",

        "coverage":
            "Per family per year",

        "treatment":
            "Secondary and tertiary hospitalization",

        "facility":
            "Cashless treatment",

        "eligibility":
            "Eligible PM-JAY beneficiaries",

        "line1":
            "Health cover Rs 5L",

        "line2":
            "Per family per year"
    },


    # -------------------------------------------------
    # 3. UJJWALA
    # -------------------------------------------------

    {
        "title": "UJJWALA",

        "full_name":
            "Pradhan Mantri Ujjwala Yojana",

        "purpose":
            "Provide clean LPG cooking fuel",

        "benefit":
            "Deposit-free LPG connection",

        "eligibility":
            "Adult woman from eligible poor household",

        "condition":
            "No existing LPG connection in household",

        "line1":
            "Deposit-free LPG",

        "line2":
            "For eligible women"
    },


    # -------------------------------------------------
    # 4. PM AWAS
    # -------------------------------------------------

    {
        "title": "PM AWAS",

        "full_name":
            "Pradhan Mantri Awaas Yojana-Gramin",

        "purpose":
            "Provide pucca houses in rural areas",

        "benefit":
            "Rs 1.20 lakh in plain areas",

        "hilly_benefit":
            "Rs 1.30 lakh in specified hilly/NE areas",

        "house_size":
            "Minimum 25 square metres",

        "labour":
            "90/95 days MGNREGS labour support",

        "toilet":
            "Rs 12000 toilet assistance",

        "eligibility":
            "Eligible rural households",

        "line1":
            "Rs 1.20L / Rs 1.30L",

        "line2":
            "Rural housing support"
    },


    # -------------------------------------------------
    # 5. PM SVANIDHI
    # -------------------------------------------------

    {
        "title": "PM SVANIDHI",

        "full_name":
            "PM Street Vendor's AtmaNirbhar Nidhi",

        "purpose":
            "Working-capital support for street vendors",

        "loan1":
            "First loan up to Rs 15000",

        "loan2":
            "Second loan up to Rs 25000",

        "loan3":
            "Third loan up to Rs 50000",

        "interest":
            "7 percent interest subsidy",

        "collateral":
            "Collateral-free working capital",

        "digital":
            "Cashback for eligible digital transactions",

        "eligibility":
            "Eligible street vendors",

        "line1":
            "Loans up to Rs 50K",

        "line2":
            "For street vendors"
    }

]


# =====================================================
# SERIAL
# =====================================================

print()
print("=" * 60)
print("NAYAK SCHEME SELECTOR")
print("=" * 60)

print()
print("Connecting to ESP32...")

ser = serial.Serial(
    PORT,
    BAUD,
    timeout=1
)

# Give ESP32 time to reset
time.sleep(2)

# Clear anything left from previous run
ser.reset_input_buffer()

print("ESP32 connected!")


# =====================================================
# SEND COMMAND
# =====================================================

def send_command(command):

    message = command + "\n"

    ser.write(
        message.encode("utf-8")
    )

    ser.flush()


# =====================================================
# DISPLAY SCHEME
# =====================================================

def display_scheme(index):

    scheme = SCHEMES[index]

    title = scheme["title"]
    line1 = scheme["line1"]
    line2 = scheme["line2"]

    print()
    print("-" * 60)
    print(
        f"SCHEME {index + 1} / {len(SCHEMES)}"
    )
    print(title)
    print(line1)
    print(line2)
    print("-" * 60)

    # -------------------------------------------------
    # Protocol:
    #
    # DISPLAY
    # title
    # line1
    # line2
    #
    # -------------------------------------------------

    send_command("DISPLAY")

    send_command(title)
    send_command(line1)
    send_command(line2)


# =====================================================
# WAIT FOR ESP32 READY
# =====================================================

print()
print("Waiting for ESP32 READY...")

ready = False

timeout = time.time() + 8

while time.time() < timeout:

    line = ser.readline()

    if not line:
        continue

    text = line.decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if text:

        print(
            "ESP32:",
            text
        )

    if text == "READY":

        ready = True
        break


if not ready:

    print()
    print(
        "ERROR: ESP32 did not send READY."
    )

    ser.close()

    raise SystemExit


# =====================================================
# SHOW FIRST SCHEME
# =====================================================

current_scheme = 0

display_scheme(
    current_scheme
)


print()
print("=" * 60)
print("SCHEME SELECTOR READY")
print("=" * 60)
print()
print("BUTTON 1 = NEXT")
print("BUTTON 2 = SELECT")
print()


# =====================================================
# MAIN LOOP
# =====================================================

try:

    while True:

        line = ser.readline()

        if not line:
            continue


        text = line.decode(
            "utf-8",
            errors="ignore"
        ).strip()


        if not text:
            continue


        # =================================================
        # NEXT BUTTON
        # =================================================

        if text == "NEXT":

            current_scheme += 1

            if current_scheme >= len(SCHEMES):

                current_scheme = 0


            display_scheme(
                current_scheme
            )

            continue


        # =================================================
        # SELECT BUTTON
        # =================================================

        if text == "SELECT":

            selected = SCHEMES[
                current_scheme
            ]

            print()
            print("=" * 60)
            print("SCHEME SELECTED")
            print("=" * 60)

            print(
                f"Number: {current_scheme + 1}"
            )

            print(
                f"Title: {selected['title']}"
            )

            print(
                f"{selected['line1']}"
            )

            print(
                f"{selected['line2']}"
            )

            print("=" * 60)
            print()


except KeyboardInterrupt:

    print()
    print("Stopping...")


finally:

    ser.close()