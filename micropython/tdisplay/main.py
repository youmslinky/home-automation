import time
import random
import machine
from machine import Pin
import st7789py
import framebuf

#attach interrupts to button pins
count = 0

button_pin_1 = Pin(0, Pin.IN, Pin.PULL_UP)
button_pin_2 = Pin(35, Pin.IN, Pin.PULL_UP)

def button1_callback(p):
    global count
    if p.value() == 0:
        count += 1
    else:
        pass

def button2_callback(p):
    global count
    if p.value() == 0:
        count -= 1
    else:
        pass

button_pin_1.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button1_callback)
button_pin_2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button2_callback)

# turn on backlight
bl = machine.Pin(4, machine.Pin.OUT)
bl.value(1)

spi = machine.SPI(
    2,
    baudrate=20000000,
    polarity=1,
    phase=1,
    sck=machine.Pin(18),
    mosi=machine.Pin(19),
    miso=machine.Pin(17))

display = st7789py.ST7789(
    spi, 135, 240,
    reset=machine.Pin(23, machine.Pin.OUT),
    cs=machine.Pin(5, machine.Pin.OUT),
    dc=machine.Pin(16, machine.Pin.OUT))

display.init()

# while True:
    # display.pixel(
    #     random.randint(50,80),
    #     random.randint(50,80),
    #     st7789py.color565(
    #         random.getrandbits(8),
    #         random.getrandbits(8),
    #         random.getrandbits(8),
    #     ),
    # )
# for i in range(135):
#     for j in range(240):
#         display.pixel(i,j,st7789py.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

def rand_color():
    return st7789py.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

import hack32_h as font
def gen_bits(memap):
    for b in memap:
        for offset in range(8):
            yield (b<<offset) & (1<<7)

class writer:
    cursor_x = 0
    cursor_y = 0
    display_width = 135
    display_height = 240

    def carriage_return(self):
        self.cursor_x = 0
    def newline(self):
        self.cursor_y += font.height()

    def write_char(self,x,y,char_h,char_w,char_mem, color=st7789py.WHITE, bg_color=st7789py.BLACK):
        if bg_color == 'random_ch':
            bg_color = rand_color()
        if color == 'random_ch':
            color = rand_color()
        #blank out area we want to draw our character
        display.fill_rect(x,y,char_w,char_h,bg_color)
        gb = gen_bits(char_mem)
        for col in range(char_w):
            for row in range(char_h):
                if(next(gb)):
                    display.pixel(col+x, row+y, color)

    def print(self, string, color=st7789py.WHITE, bg_color=st7789py.BLACK):
        if color == 'random':
            color = rand_color()
        if bg_color == 'random':
            bg_color = rand_color()
        for ch in string:
            if ch == '\r':
                self.carriage_return()
                continue
            if ch == '\n':
                self.newline()
                continue
            char_mem, char_h, char_w = font.get_ch(ch)
            if self.cursor_x + char_w > self.display_width:
                self.carriage_return()
                self.newline()
            self.write_char(self.cursor_x, self.cursor_y, char_h, char_w, char_mem, color = color, bg_color = bg_color)
            self.cursor_x += char_w

class new_writer:
    cursor_x = 0
    cursor_y = 0
    display_width = 135
    display_height = 240

    def carriage_return(self):
        self.cursor_x = 0
    def newline(self):
        self.cursor_y += font.height()

    def binbuffTo565(self,buf):
        mybuf = bytearray(len(buf)*8*2)
        mybuf_index = 0
        for byte in buf:
            for shift in range(8):
                if (byte<<shift)&(1<<7):
                #if (byte>>shift)&(1):
                    mybuf[mybuf_index] = 0x55
                    mybuf[mybuf_index+1] = 0x55
                else:
                    mybuf[mybuf_index] = 0x00
                    mybuf[mybuf_index+1] = 0x00
                mybuf_index += 2
        print("ending mybuf_index: ", mybuf_index)
        print("len(mybuf) ", len(mybuf))
        return mybuf

    def write_char(self,x,y,char_h,char_w,char_mem, color=st7789py.WHITE, bg_color=st7789py.BLACK):
        if bg_color == 'random_ch':
            bg_color = rand_color()
        if color == 'random_ch':
            color = rand_color()
        buf = self.binbuffTo565(char_mem)
        display.blit_buffer(buf,x,y,char_w,char_h)

    def print(self, string, color=st7789py.WHITE, bg_color=st7789py.BLACK):
        if color == 'random':
            color = rand_color()
        if bg_color == 'random':
            bg_color = rand_color()
        for ch in string:
            if ch == '\r':
                self.carriage_return()
                continue
            if ch == '\n':
                self.newline()
                continue
            char_mem, char_h, char_w = font.get_ch(ch)
            print("char:",ch)
            print("using len:",len(char_mem))
            print("using h*w:",char_h*char_w)
            if self.cursor_x + char_w > self.display_width:
                self.carriage_return()
                self.newline()
            self.write_char(self.cursor_x, self.cursor_y, char_h, char_w, char_mem, color = color, bg_color = bg_color)
            self.cursor_x += char_w

def binbuffTo565(buf):
    mybuf = bytearray(len(buf)*8*2)
    mybuf_index = 0
    for byte in buf:
        for shift in range(8):
            if (byte>>shift)&(1):
                mybuf[mybuf_index] = 0xff
                mybuf[mybuf_index+1] = 0xff
            mybuf_index += 2
    return mybuf

char_mem, char_h, char_w = font.get_ch('%')
buf = binbuffTo565(char_mem)
display.blit_buffer(buf,50,150,char_h,char_w)

w = new_writer()
w.cursor_x = 0
w.cursor_y = 0
w.print('sphinx of black quartz, judge my vow')

w = writer()
w.cursor_x = 0
w.cursor_y = 0
w.print('sphinx of black quartz, judge my vow')


# w.print('random\n', color = 'random_ch')
# for i in range(10**7):
#     w.print(str(i)+'\r', color = 'random')
# while True:
#     w.print(str(count)+'\r')

