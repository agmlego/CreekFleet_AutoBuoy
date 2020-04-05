from datetime import datetime
from time import sleep

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
print('Radio %s'%radio_sn)

while True:
    sleep(1)
    radio.write(b'+++')
    sleep(1)
    radio.read(3)
    radio.write(b'ATDB\r')
    rssi = -int(radio.read(3)[:-1],base=16)
    radio.write(b'ATCN\r')
    radio.read(3)

    me_lat=agps3.data_stream.lat
    me_lon=agps3.data_stream.lon
    rem_lat=me_lat  # TODO maybe actually get remote lat-long
    rem_lon=me_lon
    with canvas(dev) as draw:
        draw.text((0,0),'%s - %s'%(
            datetime.strptime(
                agps3.data_stream.time,
                '%Y-%m-%dT%H:%M:%S.%fZ').time().isoformat(),
            radio_sn),fill='white')
        draw.text((0,12),'Me:%0.5f,%0.5f'%(me_lat,me_lon),fill='white')
        draw.text((0,24),'RM:%0.5f,%0.5f'%(rem_lat,rem_lon),fill='white')
        draw.text((0,36),'RSSI:%4d'%(rssi,),fill='white')