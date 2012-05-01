from ctypes import *

dll = CDLL('_emulator')

class cEmulator(Structure):
    _fields_ = [
        ('ram', c_ushort * 0x10010),
        ('skip', c_ushort),
        ('halt', c_ushort),
        ('cycle', c_ulonglong),
        ('interrupt_buffer', c_ushort * 256),
        ('interrupt_index', c_ushort),
        ('interrupt_queueing', c_ushort),
        ('lem_screen', c_ushort),
        ('lem_font', c_ushort),
        ('lem_palette', c_ushort),
        ('lem_border', c_ushort),
        ('keyboard_buffer', c_ubyte * 16),
        ('keyboard_pressed', c_ubyte * 256),
        ('keyboard_index', c_ushort),
        ('keyboard_message', c_ushort),
        ('clock_cycle', c_ulonglong),
        ('clock_rate', c_ushort),
        ('clock_ticks', c_ushort),
        ('clock_message', c_ushort),
    ]

FIELDS = set(x[0] for x in cEmulator._fields_)

class Emulator(object):
    def __init__(self):
        self.emulator = cEmulator()
        self.reset()
    def __getattr__(self, name):
        if name in FIELDS:
            return getattr(self.emulator, name)
        return super(Emulator, self).__getattr__(name)
    def __setattr__(self, name, value):
        if name in FIELDS:
            return setattr(self.emulator, name, value)
        return super(Emulator, self).__setattr__(name, value)
    def reset(self):
        dll.reset(byref(self.emulator))
    def load(self, program):
        self.reset()
        length = len(program)
        data = (c_ushort * length)()
        for index, value in enumerate(program):
            data[index] = value
        dll.load(byref(self.emulator), data, length)
    def step(self):
        dll.step(byref(self.emulator))
    def n_steps(self, steps):
        dll.n_steps(byref(self.emulator), steps)
    def n_cycles(self, cycles):
        dll.n_cycles(byref(self.emulator), cycles)
    def on_key_down(self, key):
        dll.on_key_down(byref(self.emulator), key)
    def on_key_up(self, key):
        dll.on_key_up(byref(self.emulator), key)
    def on_char(self, key):
        dll.on_char(byref(self.emulator), key)
