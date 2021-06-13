from machine import Pin, I2C
import ssd1306
from time import sleep
from utime import time
import machine

# ESP32 Pin assignment
i2c = I2C(-1, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


button_pin = Pin(34, Pin.IN, Pin.PULL_UP)
pir_pin = Pin(33, Pin.IN)

# flags for signaling from interrupt to main while loop
button_event = False
button_rise = False
pir_event = False
pir_rise = False

screen_last_display_time = time()
last_sensor_config_time = time()

def button_change_inter(p):
    global button_event
    global button_rise
    global screen_last_display_time
    screen_last_display_time = time()
    oled.fill(0)
    if p.value() == 0:
        oled.text("button pressed", 0, 0)
        button_rise = False
    else:
        oled.text("button released", 0, 0)
        button_rise = True
    oled.show()
    button_event = True


def pir_change_inter(p):
    global pir_event
    global pir_rise
    global screen_last_display_time
    screen_last_display_time = time()
    oled.fill(0)
    if p.value() == 0:
        oled.text("pir: nothing", 0, 0)
        pir_rise = False
    else:
        oled.text("pir: detected", 0, 0)
        pir_rise = True
    oled.show()
    pir_event = True


button_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_change_inter)
pir_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=pir_change_inter)


def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b"notification" and msg == b"received":
        print("ESP received hello message")


def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print(
        "Connected to %s MQTT broker, subscribed to %s topic" % (mqtt_server, topic_sub)
    )
    return client


def restart_and_reconnect():
    print("Failed to connect to MQTT broker. Reconnecting...")
    time.sleep(10)
    machine.reset()


bin_topic_header = b"homeassistant/binary_sensor/espcam"
bin_sensors_dict = {
    b"button": b"""{"name": "button", "state_topic": "homeassistant/binary_sensor/espcam/button/state"}""",
    b"pir": b"""{"name": "pir", "device_class": "motion", "state_topic": "homeassistant/binary_sensor/espcam/pir/state"}""",
}


def setup_hass_mqtt_bin_sensors():
    # initialize sensors with hass mqtt discovery
    for sensor_name, config_payload in bin_sensors_dict.items():
        topic = bin_topic_header + b"/" + sensor_name + "/config"
        client.publish(topic, config_payload)


try:
    client = connect_and_subscribe()
    setup_hass_mqtt_bin_sensors()
except OSError as e:
    print(e)
    restart_and_reconnect()


while True:
    t = time()
    if t - last_sensor_config_time > 43200: #12hours (12*60*60 seconds)
        # every 12 hours, send a config command, so home assistant is updated,
        # not sure how to do this on events, like hass boot up.  maybe hass sends
        # a mqtt boot up message on mqtt?
        setup_hass_mqtt_bin_sensors()
        last_sensor_config_time = time()

    if t - screen_last_display_time > 3:
        #blank display if on longer than x sec
        oled.fill(0)
        oled.show()
    try:
        client.check_msg()
        if button_event:
            if button_rise:
                msg = b"OFF"
            else:
                msg = b"ON"
            topic = bin_topic_header + b"/button/state"
            client.publish(topic, msg)
            button_event = False
        if pir_event:
            if pir_rise:
                msg = b"ON"
            else:
                msg = b"OFF"
            topic = bin_topic_header + b"/pir/state"
            client.publish(topic, msg)
            pir_event = False
    except OSError as e:
        print(e)
        restart_and_reconnect()
