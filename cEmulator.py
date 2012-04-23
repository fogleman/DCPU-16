from ctypes import *

dll = CDLL('_emulator')

EXT_SIZE = 0x1000c

class cEmulator(Structure):
    _fields_ = [
        ('ram', POINTER(c_ushort)),
        ('skip', c_uint),
        ('halt', c_uint),
        ('cycle', c_uint),
    ]

class Emulator(object):
    def __init__(self):
        self.emulator = cEmulator()
        self.emulator.ram = (c_ushort * EXT_SIZE)()
        self.ram = self.emulator.ram
        self.reset()
    def reset(self):
        dll.reset(byref(self.emulator))
    def load(self, program):
        self.reset()
        length = len(program)
        data = (c_ushort * length)()
        for index, value in enumerate(program):
            data[index] = value
        dll.load(byref(self.emulator), data, length)
    def n_cycles(self, cycles):
        dll.n_cycles(byref(self.emulator), cycles)
    def step(self):
        dll.step(byref(self.emulator))
