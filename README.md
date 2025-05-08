# jk-pb-cellvolts
Simple solution to read all the cell voltages via RS485 Modbus and publish them to MQTT 

using read_holding_registers(), not the JK App method do write/trigger a register and receive lots ob bytes.

Most likely there are more infos you might gain this way from other registers, but I was interested in the cell voltages, only.

## Requirements
- pymodbus
- paho-mqtt

You may leave out MQTT, simply get voltages put out on screen. Comment out the two lines.




