# voxpop Messenger - Hardware Prototype

This document outlines the hardware components and assembly instructions for the initial prototype of the `voxpop` single-message, anonymous messenger device. This prototype focuses on functionality and core anonymity features, not aesthetics.

## Goals

*   **Functionality:** Send a single, encrypted message via Wi-Fi.
*   **Anonymity:** Minimize traceability through MAC address randomization and ephemeral data storage.
*   **Simplicity:** Use readily available and inexpensive components.
*   **Testability:** Design for easy testing and modification.

## Components

| Component                     | Description                                                                                                | Quantity | Notes                                                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------- |
| ESP32 Development Board       | NodeMCU-32S, ESP32-WROOM-32 DevKitC, or similar. Provides Wi-Fi and microcontroller.                      | 1        | Ensure it has built-in Wi-Fi.                                                                                            |
| OLED Display                  | 128x64 pixels, SSD1306 driver.  Displays messages and status.                                                 | 1        | I2C interface is recommended for simplicity.                                                                          |
| 4x4 Membrane Keypad          | Provides user input for message and Wi-Fi credentials.                                                    | 1        |                                                                                                                        |
| Breadboard                    | For connecting components without soldering.                                                                 | 1        | A half-size or full-size breadboard is sufficient.                                                                  |
| Jumper Wires                 | Male-to-Male and Male-to-Female. For connecting components.                                                     | Assorted | A variety pack is recommended.                                                                                        |
| Battery Holder                | 2 x AA battery holder.                                                                                    | 1        | Provides power for standalone operation.                                                                               |
| AA Batteries                 | Alkaline batteries.                                                                                         | 2        |                                                                                                                        |
| USB Cable                    | Micro-USB or USB-C (depends on ESP32 board). For programming and power during development.                  | 1        |                                                                                                                        |
| 10kΩ Resistors | Pull-up or Pull-down | 5 |

## Assembly Instructions

**1. Component Testing (Highly Recommended):**

Before assembling the full prototype, test each component individually using simple Arduino sketches.  This will save you a lot of troubleshooting time later.

*   **ESP32:** Test basic Wi-Fi connection and serial communication.
*   **OLED Display:** Test displaying text and graphics using a library like `Adafruit_SSD1306`.
*   **Keypad:** Test reading key presses using a library like `Keypad`.

**2. Wiring Diagram:**

The following wiring diagram describes the connections between the components.  Use the breadboard and jumper wires to make the connections.

   *   **ESP32 to OLED Display (SSD1306):**

        *   `ESP32 3.3V`  ->  `OLED VCC`
        *   `ESP32 GND`   ->  `OLED GND`
        *   `ESP32 GPIO22` (SCL) ->  `OLED SCL`
        *   `ESP32 GPIO21` (SDA) ->  `OLED SDA`

   *   **ESP32 to 4x4 Keypad:**

        *   `ESP32 GPIO19` -> `Keypad Row 1`
        *   `ESP32 GPIO18` -> `Keypad Row 2`
        *   `ESP32 GPIO5`  -> `Keypad Row 3`
        *   `ESP32 GPIO17` -> `Keypad Row 4`
        *   `ESP32 GPIO16` -> `Keypad Column 1`
        *   `ESP32 GPIO4`  -> `Keypad Column 2`
        *   `ESP32 GPIO0`  -> `Keypad Column 3`
        *   `ESP32 GPIO2`  -> `Keypad Column 4`
        *    Resistors (10 kOhm) are connected between each column pin and ground

   * **ESP32 to Battery Holder (Optional - for standalone operation):**
        *  `Battery Holder (+)` -> `ESP32 Vin` (or `5V` pin)
        *  `Battery Holder (-)` -> `ESP32 GND`

**Important Notes:**

*   **GPIO Pin Numbers:** The pin numbers above are *examples*.  You can use different GPIO pins on the ESP32 if needed, but you'll need to update the code accordingly.  Avoid using pins that have special functions (e.g., pins used for flashing the ESP32).
*   **Power:** When connected via USB, the ESP32 is powered by the USB connection.  When using batteries, connect the battery holder to the `Vin` (or `5V`) and `GND` pins of the ESP32.  *Do not connect both USB and batteries at the same time unless your ESP32 board has built-in power management to handle this.*
* **Resistors**: Add 10kOhm resistors.

**3. Software:**

The software for the hardware prototype is located in the `firmware/` directory (or similar - adjust the path as needed).  See the `firmware/README.md` file for instructions on compiling and uploading the code to the ESP32.

**4. Testing:**

Once the hardware is assembled and the software is uploaded, test the device by:

1.  Powering on the device (either via USB or batteries).
2.  Entering the Wi-Fi SSID and password using the keypad.
3.  Entering the message using the keypad.
4.  Sending the message.
5.  Verifying that the message appears on the public display (website).
6. Verify that the MAC address randomization working correctly.

**5. Anonymity Considerations:**

*   **MAC Address Randomization:** The firmware includes code to randomize the ESP32's MAC address on each boot. This is crucial for anonymity.
*   **Public Wi-Fi:** It is strongly recommended to use a public Wi-Fi network (not your home network) when sending messages to further enhance anonymity.
*   **No Persistent Storage:** The device does not store the Wi-Fi credentials or the message after sending.

This README provides a starting point for building the hardware prototype. Remember to consult the datasheets for your specific components for more detailed information. Good luck!
