from ctypes import *

dll = CDLL('_emulator')

EXT_SIZE = 0x1000d

class cEmulator(Structure):
    _fields_ = [
        ('ram', POINTER(c_ushort)),
        ('skip', c_uint),
        ('cycle', c_ulonglong),
        ('lem1802_screen', c_ushort),
        ('lem1802_font', c_ushort),
        ('lem1802_palette', c_ushort),
        ('lem1802_border', c_ushort),
    ]

ATTRS = set([x[0] for x in cEmulator._fields_])

class Emulator(object):
    def __init__(self):
        self.emulator = cEmulator()
        self.emulator.ram = (c_ushort * EXT_SIZE)()
        self.reset()
    def __getattr__(self, name):
        if name in ATTRS:
            return getattr(self.emulator, name)
        return super(Emulator, self).__getattr__(name)
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
