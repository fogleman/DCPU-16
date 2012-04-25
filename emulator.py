import struct

# Constants
SIZE = 0x10000
MAX_VALUE = 0xffff
EXT_SIZE = 0x1000d
REGISTER = 0x10000
SP = 0x10008
PC = 0x10009
EX = 0x1000a
IA = 0x1000b
LT = 0x1000c

# Lookups
REGISTERS = 'ABCXYZIJ'

BASIC_OPCODES = {
    0x01: 'SET',
    0x02: 'ADD',
    0x03: 'SUB',
    0x04: 'MUL',
    0x05: 'MLI',
    0x06: 'DIV',
    0x07: 'DVI',
    0x08: 'MOD',
    0x09: 'AND',
    0x0a: 'BOR',
    0x0b: 'XOR',
    0x0c: 'SHR',
    0x0d: 'ASR',
    0x0e: 'SHL',
    0x0f: 'MVI',
    0x10: 'IFB',
    0x11: 'IFC',
    0x12: 'IFE',
    0x13: 'IFN',
    0x14: 'IFG',
    0x15: 'IFA',
    0x16: 'IFL',
    0x17: 'IFU',
    0x1a: 'ADX',
    0x1b: 'SUX',
}

SPECIAL_OPCODES = {
    0x01: 'JSR',
    0x08: 'INT',
    0x09: 'IAG',
    0x0a: 'IAS',
    0x10: 'HWN',
    0x11: 'HWQ',
    0x12: 'HWI',
}

GLYPHS = [
    0x000f, 0x0808, 0x080f, 0x0808, 0x08f8, 0x0808, 0x00ff, 0x0808,
    0x0808, 0x0808, 0x08ff, 0x0808, 0x00ff, 0x1414, 0xff00, 0xff08,
    0x1f10, 0x1714, 0xfc04, 0xf414, 0x1710, 0x1714, 0xf404, 0xf414,
    0xff00, 0xf714, 0x1414, 0x1414, 0xf700, 0xf714, 0x1417, 0x1414,
    0x0f08, 0x0f08, 0x14f4, 0x1414, 0xf808, 0xf808, 0x0f08, 0x0f08,
    0x001f, 0x1414, 0x00fc, 0x1414, 0xf808, 0xf808, 0xff08, 0xff08,
    0x14ff, 0x1414, 0x080f, 0x0000, 0x00f8, 0x0808, 0xffff, 0xffff,
    0xf0f0, 0xf0f0, 0xffff, 0x0000, 0x0000, 0xffff, 0x0f0f, 0x0f0f,
    0x0000, 0x0000, 0x005f, 0x0000, 0x0300, 0x0300, 0x3e14, 0x3e00,
    0x266b, 0x3200, 0x611c, 0x4300, 0x3629, 0x7650, 0x0002, 0x0100,
    0x1c22, 0x4100, 0x4122, 0x1c00, 0x2a1c, 0x2a00, 0x083e, 0x0800,
    0x4020, 0x0000, 0x0808, 0x0800, 0x0040, 0x0000, 0x601c, 0x0300,
    0x3e41, 0x3e00, 0x427f, 0x4000, 0x6259, 0x4600, 0x2249, 0x3600,
    0x0f08, 0x7f00, 0x2745, 0x3900, 0x3e49, 0x3200, 0x6119, 0x0700,
    0x3649, 0x3600, 0x2649, 0x3e00, 0x0024, 0x0000, 0x4024, 0x0000,
    0x0814, 0x2241, 0x1414, 0x1400, 0x4122, 0x1408, 0x0259, 0x0600,
    0x3e59, 0x5e00, 0x7e09, 0x7e00, 0x7f49, 0x3600, 0x3e41, 0x2200,
    0x7f41, 0x3e00, 0x7f49, 0x4100, 0x7f09, 0x0100, 0x3e49, 0x3a00,
    0x7f08, 0x7f00, 0x417f, 0x4100, 0x2040, 0x3f00, 0x7f0c, 0x7300,
    0x7f40, 0x4000, 0x7f06, 0x7f00, 0x7f01, 0x7e00, 0x3e41, 0x3e00,
    0x7f09, 0x0600, 0x3e41, 0xbe00, 0x7f09, 0x7600, 0x2649, 0x3200,
    0x017f, 0x0100, 0x7f40, 0x7f00, 0x1f60, 0x1f00, 0x7f30, 0x7f00,
    0x7708, 0x7700, 0x0778, 0x0700, 0x7149, 0x4700, 0x007f, 0x4100,
    0x031c, 0x6000, 0x0041, 0x7f00, 0x0201, 0x0200, 0x8080, 0x8000,
    0x0001, 0x0200, 0x2454, 0x7800, 0x7f44, 0x3800, 0x3844, 0x2800,
    0x3844, 0x7f00, 0x3854, 0x5800, 0x087e, 0x0900, 0x4854, 0x3c00,
    0x7f04, 0x7800, 0x447d, 0x4000, 0x2040, 0x3d00, 0x7f10, 0x6c00,
    0x417f, 0x4000, 0x7c18, 0x7c00, 0x7c04, 0x7800, 0x3844, 0x3800,
    0x7c14, 0x0800, 0x0814, 0x7c00, 0x7c04, 0x0800, 0x4854, 0x2400,
    0x043e, 0x4400, 0x3c40, 0x7c00, 0x1c60, 0x1c00, 0x7c30, 0x7c00,
    0x6c10, 0x6c00, 0x4c50, 0x3c00, 0x6454, 0x4c00, 0x0836, 0x4100,
    0x0077, 0x0000, 0x4136, 0x0800, 0x0201, 0x0201, 0x704c, 0x7000,
]

# Helper Functions
def signed(x):
    return struct.unpack('<h', struct.pack('<H', x))[0]

# Emulator
class Emulator(object):
    def __init__(self):
        self.basic_opcodes = {}
        self.special_opcodes = {}
        for key, value in BASIC_OPCODES.items():
            self.basic_opcodes[key] = getattr(self, value)
        for key, value in SPECIAL_OPCODES.items():
            self.special_opcodes[key] = getattr(self, value)
        self.reset()
    # Helper Properties
    @property
    def pc(self):
        return self.ram[PC]
    @pc.setter
    def pc(self, x):
        self.ram[PC] = x
    @property
    def sp(self):
        return self.ram[SP]
    @sp.setter
    def sp(self, x):
        self.ram[SP] = x
    @property
    def ex(self):
        return self.ram[EX]
    @ex.setter
    def ex(self, x):
        self.ram[EX] = x
    @property
    def ia(self):
        return self.ram[IA]
    @ia.setter
    def ia(self, x):
        self.ram[IA] = x
    @property
    def lt(self):
        return self.ram[LT]
    @lt.setter
    def lt(self, x):
        self.ram[LT] = x
    # Initialization Functions
    def reset(self):
        self.ram = [0] * EXT_SIZE
        self.skip = False
        self.cycle = 0
        for index, value in enumerate(GLYPHS):
            self.ram[0x8180 + index] = value
    def load(self, program):
        self.reset()
        for index, value in enumerate(program):
            self.ram[index] = value
    # Run Functions
    def next_word(self, cycles=0):
        word = self.ram[self.pc]
        self.pc = (self.pc + 1) % SIZE
        self.cycle += cycles
        return word
    def step(self):
        word = self.next_word()
        op = word & 0x1f
        dst = (word >> 5) & 0x1f
        src = (word >> 10) & 0x3f
        if op:
            self.basic_instruction(op, dst, src)
        else:
            self.special_instruction(dst, src)
    def n_steps(self, steps):
        for _ in xrange(steps):
            self.step()
    def n_cycles(self, cycles):
        cycle = self.cycle + cycles
        while self.cycle < cycle:
            self.step()
    def basic_instruction(self, op, dst, src):
        src = self.operand(src, True)
        dst = self.operand(dst, False)
        if self.skip:
            self.skip = False
        else:
            func = self.basic_opcodes[op]
            self.cycle += func(self.ram[dst], dst, src)
    def special_instruction(self, op, dst):
        dst = self.operand(dst, False)
        if self.skip:
            self.skip = False
        else:
            func = self.special_opcodes[op]
            self.cycle += func(self.ram[dst], dst)
    def operand(self, x, dereference):
        literal = False
        if x < 8: # register
            result = REGISTER + x
        elif 0x08 <= x <= 0x0f: # [register]
            result = self.ram[REGISTER + x - 0x08]
        elif 0x10 <= x <= 0x17: # [register + next word]
            word = self.next_word(int(not self.skip))
            result = self.ram[REGISTER + x - 0x10] + word
        elif x == 0x18 and dereference: # POP [SP++]
            result = self.sp
            if not self.skip:
                self.sp = (self.sp + 1) % SIZE
        elif x == 0x18 and not dereference: # PUSH [--SP]
            if not self.skip:
                self.sp = (self.sp - 1) % SIZE
            result = self.sp
        elif x == 0x19: # PEEK [SP]
            result = self.sp
        elif x == 0x1a: # PICK [SP + next word]
            word = self.next_word(int(not self.skip))
            result = self.sp + word
        elif x == 0x1b: # SP
            result = SP
        elif x == 0x1c: # PC
            result = PC
        elif x == 0x1d: # EX
            result = EX
        elif x == 0x1e: # [next word]
            word = self.next_word(int(not self.skip))
            result = word
        elif x == 0x1f: # literal (next word)
            literal = True
            word = self.next_word(int(not self.skip))
            result = word
        elif x == 0x20: # literal (constant)
            literal = True
            result = 0xffff
        elif x >= 0x21: # literal (constant)
            literal = True
            result = x - 0x21
        if literal and not dereference:
            self.lt = result
            result = LT
        if dereference and not literal:
            result = self.ram[result]
        return result
    # Opcode Functions
    def SET(self, ram, dst, src):
        self.ram[dst] = src
        return 1
    def ADD(self, ram, dst, src):
        ex, self.ram[dst] = divmod(ram + src, SIZE)
        self.ex = 1 if ex else 0
        return 2
    def SUB(self, ram, dst, src):
        ex, self.ram[dst] = divmod(ram - src, SIZE)
        self.ex = MAX_VALUE if ex else 0
        return 2
    def MUL(self, ram, dst, src):
        ex, self.ram[dst] = divmod(ram * src, SIZE)
        self.ex = ex % SIZE
        return 2
    def MLI(self, ram, dst, src):
        ex, self.ram[dst] = divmod(signed(ram) * signed(src), SIZE)
        self.ex = ex % SIZE
        return 2
    def DIV(self, ram, dst, src):
        if src:
            self.ex = ((ram << 16) / src) % SIZE
            self.ram[dst] = (ram / src) % SIZE
        else:
            self.ram[dst] = 0
            self.ex = 0
        return 3
    def DVI(self, ram, dst, src):
        if src:
            ram = signed(ram)
            src = signed(src)
            self.ex = ((ram << 16) / src) % SIZE
            self.ram[dst] = (ram / src) % SIZE
        else:
            self.ram[dst] = 0
            self.ex = 0
        return 3
    def MOD(self, ram, dst, src):
        if src:
            self.ram[dst] %= src
        else:
            self.ram[dst] = 0
        return 3
    def AND(self, ram, dst, src):
        self.ram[dst] = (ram & src) % SIZE
        return 1
    def BOR(self, ram, dst, src):
        self.ram[dst] = (ram | src) % SIZE
        return 1
    def XOR(self, ram, dst, src):
        self.ram[dst] = (ram ^ src) % SIZE
        return 1
    def SHR(self, ram, dst, src):
        self.ex = ((ram << 16) >> src) % SIZE
        self.ram[dst] = (ram >> src) % SIZE
        return 2
    def ASR(self, ram, dst, src):
        ram = signed(ram)
        self.ex = ((ram << 16) >> src) % SIZE
        self.ram[dst] = (ram >> src) % SIZE
        return 2
    def SHL(self, ram, dst, src):
        self.ex = ((ram << src) >> 16) % SIZE
        self.ram[dst] = (ram << src) % SIZE
        return 2
    def MVI(self, ram, dst, src):
        self.ram[dst] = src
        self.ram[REGISTER + 6] = (self.ram[REGISTER + 6] + 1) % SIZE
        self.ram[REGISTER + 7] = (self.ram[REGISTER + 7] + 1) % SIZE
        return 2
    def IFB(self, ram, dst, src):
        self.skip = not ((ram & src) != 0)
        return 2 + int(self.skip)
    def IFC(self, ram, dst, src):
        self.skip = not ((ram & src) == 0)
        return 2 + int(self.skip)
    def IFE(self, ram, dst, src):
        self.skip = not (ram == src)
        return 2 + int(self.skip)
    def IFN(self, ram, dst, src):
        self.skip = not (ram != src)
        return 2 + int(self.skip)
    def IFG(self, ram, dst, src):
        self.skip = not (ram > src)
        return 2 + int(self.skip)
    def IFA(self, ram, dst, src):
        self.skip = not (signed(ram) > signed(src))
        return 2 + int(self.skip)
    def IFL(self, ram, dst, src):
        self.skip = not (ram < src)
        return 2 + int(self.skip)
    def IFU(self, ram, dst, src):
        self.skip = not (signed(ram) < signed(src))
        return 2 + int(self.skip)
    def ADX(self, ram, dst, src):
        ex, self.ram[dst] = divmod(ram + src + self.ex, SIZE)
        self.ex = 1 if ex else 0
        return 3
    def SUX(self, ram, dst, src):
        ex, self.ram[dst] = divmod(ram - src + self.ex, SIZE)
        self.ex = MAX_VALUE if ex else 0
        return 3
    def JSR(self, ram, dst):
        self.sp = (self.sp - 1) % SIZE
        self.ram[self.sp] = self.pc
        self.pc = ram
        return 3
    def INT(self, ram, dst):
        return 4
    def IAG(self, ram, dst):
        self.ram[dst] = self.ia
        return 1
    def IAS(self, ram, dst):
        self.ia = ram
        return 1
    def HWN(self, ram, dst):
        return 2
    def HWQ(self, ram, dst):
        return 4
    def HWI(self, ram, dst):
        return 4
