# This file is executed on every boot (including wake-boot from deepsleep)
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp

esp.osdebug(None)
import gc

gc.collect()

esp.osdebug(None)
# import webrepl
# webrepl.start()


def do_connect():
    import network

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect("homenet", "smallwhitedog")
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ifconfig())


mqtt_server = "192.168.1.2"
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b"notification"
topic_pub = b"hello"

last_message = 0
message_interval = 5
counter = 0


do_connect()
