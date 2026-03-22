# This example demonstrates a simple temperature sensor peripheral.
#
# The sensor's local value is updated, and it will notify
# any connected central every 10 seconds.

import bluetooth
import random
import struct
import time
import machine
import ubinascii
from ble_advertising import advertising_payload
from micropython import const
from machine import Pin
from util import blink_n, toggle_led

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

_DEVICE_ADDR = None

class BLEHideNSeek:
    
    def __init__(self, ble, name=""):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._connections = set()
        self.state = "Searching"
        
        # Set the name of the BLE Device
        if len(name) == 0:
            name = f'Hide n Seek'
        print(f'Sensor name {name}')
        
        self._payload = advertising_payload(
            name=name, services=[_ENV_SENSE_UUID]
        )
        self._advertise()
    
    def is_connected(self):
        return len(self._connections) != 0
    
    def check_state(self):
        if not hns.is_connected() and _DEVICE_ADDR is None:
            self.state = "Searching"
        elif not hns.is_connected() and _DEVICE_ADDR is not None:
            self.state = "Hiding"
        elif hns.is_connected and _DEVICE_ADDR is not None:
            self.state = "Config"
        else:
            self.state = "Error"
    
    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            #self._connections[bytes(addr)] = conn_handle
            self._connections.add(conn_handle)
            print(f"Log: Connected to Central.")
            
            global _DEVICE_ADDR
            _DEVICE_ADDR = bytes(addr)
            
            self.state = "Config"
            
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self._connections.remove(conn_handle)
            print(f"Log: Disconnected from Central.")
            
            if self.state == "Config":
                # Finished configuring, enter hiding mode.
                self.state = "Hiding"
            else:
                # Something went wrong. Start advertising again to allow a new connection.
                global _DEVICE_ADDR
                _DEVICE_ADDR = None
                
                self._advertise()
            
            
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data
    
    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

def demo():
    ble = bluetooth.BLE()
    hns = BLEHideNSeek(ble)
    while True:
        if hns.state == "Searching":
            blink_n(3)
        elif hns.state == "Config":
            blink_n(1, duration=1)
        elif hns.state == "Hiding":
            toggle_led(1)
        
        time.sleep(0.5)

if __name__ == "__main__":
    demo()