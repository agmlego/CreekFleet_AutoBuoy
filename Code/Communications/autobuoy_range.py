from datetime import datetime
from time import sleep
import sys

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

from gps3.agps3threaded import AGPS3mechanism

import serial


print('Screen setup')
i2cport = i2c(port=1,address=0x3C)
dev = ssd1306(i2cport)

print('GPS setup')
agps3 = AGPS3mechanism()
agps3.stream_data()
agps3.run_thread()

print('Radio setup')
radio = serial.Serial('/dev/ttyAMA0',115200)
sleep(1)
radio.write(b'+++')
sleep(1)
radio.read(3)
radio.write(b'ATSH\r')
radio_sn = radio.read(5)[:-1]
radio.write(b'ATSL\r')
radio_sn += radio.read(5)[:-1]
radio.write(b'ATCN\r')
radio.read(3)
radio_sn = radio_sn.decode('utf-8')
print(f'Radio {radio_sn}')

while True:
    sleep(1)
    radio.write(b'+++')
    sleep(1)
    radio.read(3)
    radio.write(b'ATDB\r')
    raw_rssi = radio.read(3)[:-1]
    print(f'RSSI: {raw_rssi}')
    try:
        rssi = -int(raw_rssi,base=16)
    except ValueError:
        print(f'Bad RSSI: "{raw_rssi}"',sys.stderr)
        rssi = 0
    radio.write(b'ATCN\r')
    radio.read()

    me_lat=agps3.data_stream.lat
    me_lon=agps3.data_stream.lon
    rem_lat=me_lat  # TODO maybe actually get remote lat-long
    rem_lon=me_lon
    with canvas(dev) as draw:
        gps_time = datetime.strptime(
                agps3.data_stream.time,
                '%Y-%m-%dT%H:%M:%S.%fZ').time().isoformat()
        draw.text((0,0),f'{gps_time} - {radio_sn}',fill='white')
        draw.text((0,12),f'Me:{me_lat:.5f},{me_lon:.5f}',fill='white')
        draw.text((0,24),f'RM:{rem_lat:.5f},{rem_lon:.5f}',fill='white')
        draw.text((0,36),f'RSSI:{rssi:4d}',fill='white')
