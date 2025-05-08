'''
   Copyright 2025 philippoo66
   
   Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.gnu.org/licenses/gpl-3.0.html

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import signal
from time import sleep
from pymodbus.client import ModbusSerialClient

import mqtt_util

def handle_exit(sig, frame):
    raise(SystemExit)

def decode_uint16(registers, wordorder='little'):
    """
    Dekodiert eine Liste 16-bit-Register in uint16-Werte.
    """
    return [r for r in registers]

def main():

    # Signale abfangen für sauberes Beenden
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    try:
        # RS485/USB Konfiguration
        client = ModbusSerialClient(
            framer='rtu',
            port='/dev/ttyUSB0',  # adjust serial port here!
            baudrate=115200,
            timeout=1,
            stopbits=1,
            parity='N',
            bytesize=8
        )

        if not client.connect():
            print("Verbindung zum BMS fehlgeschlagen.")
            exit()

        mqtt_util.connect_mqtt()

        SLAVE_ID = 0x01
        start_register = 0x1200
        anzahl_register = 16  # 16 Zellen à 1 Register (16-bit unsigned int)

        while True:
            response = client.read_holding_registers(
                address=start_register,
                count=anzahl_register,
                slave=SLAVE_ID
            )

            if not response.isError():
                register_values = decode_uint16(response.registers)

                for i, value in enumerate(register_values):
                    voltage = value / 1000.0
                    print(f"Zelle {i + 1}: {voltage:.3f} V")
                    mqtt_util.add2queue(f"cell{i+1}", voltage)

            else:
                print("Fehler beim Lesen der Zellspannungen:", response)

            print("")
            sleep(5)

    except Exception as e:
        print("Fehler:", e)
    finally:
        client.close()
        mqtt_util.exit_mqtt()

if __name__ == "__main__":
    main()
