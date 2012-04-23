# Constants
MAX_VALUE = 0xffff
SIZE = 0x10000
REGISTER = 0x10000
SP = 0x10008
PC = 0x10009
O = 0x1000a
LIT = 0x1000b

# Lookups
REGISTERS = 'ABCXYZIJ'

BASIC_OPCODES = {
    0x1: 'SET',
    0x2: 'ADD',
    0x3: 'SUB',
    0x4: 'MUL',
    0x5: 'DIV',
    0x6: 'MOD',
    0x7: 'SHL',
    0x8: 'SHR',
    0x9: 'AND',
    0xa: 'BOR',
    0xb: 'XOR',
    0xc: 'IFE',
    0xd: 'IFN',
    0xe: 'IFG',
    0xf: 'IFB',
}

NON_BASIC_OPCODES = {
    0x0: 'BRK',
    0x1: 'JSR',
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

# Emulator
class Emulator(object):
    def __init__(self):
        self.basic_opcodes = {}
        self.non_basic_opcodes = {}
        for key, value in BASIC_OPCODES.items():
            self.basic_opcodes[key] = getattr(self, value)
        for key, value in NON_BASIC_OPCODES.items():
            self.non_basic_opcodes[key] = getattr(self, value)
        self.reset()
    # Logging Functions
    def dump(self):
        for name, value in zip(['PC', 'SP'], [self.pc, self.sp]):
            print '%s = 0x%x' % (name, value)
        for name, value in zip(REGISTERS, self.ram[REGISTER:REGISTER+8]):
            print '%s = 0x%x' % (name, value)
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
    def o(self):
        return self.ram[O]
    @o.setter
    def o(self, x):
        self.ram[O] = x
    @property
    def lit(self):
        return self.ram[LIT]
    @lit.setter
    def lit(self, x):
        self.ram[LIT] = x
    # Initialization Functions
    def reset(self):
        self.ram = [0] * (SIZE + 12)
        self.skip = False
        self.halt = False
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
        op = word & 0x000f
        a = (word & 0x03f0) >> 4
        b = (word & 0xfc00) >> 10
        if op:
            self.basic_instruction(op, a, b)
        else:
            self.non_basic_instruction(a, b)
    def n_steps(self, steps):
        for _ in xrange(steps):
            self.step()
    def n_cycles(self, cycles):
        cycle = self.cycle + cycles
        while self.cycle < cycle:
            self.step()
    def basic_instruction(self, op, a, b):
        a, _ta = self.operand(a, False)
        b, _tb = self.operand(b, True)
        func = self.basic_opcodes[op]
        if self.skip:
            self.skip = False
        else:
            #print '%04x: %s %s, %s' % (self.pc - 1, BASIC_OPCODES[op], _ta, _tb)
            self.cycle += func(a, b)
    def non_basic_instruction(self, op, a):
        a, _ta = self.operand(a, True)
        func = self.non_basic_opcodes[op]
        if self.skip:
            self.skip = False
        else:
            #print '%04x: %s %s' % (self.pc - 1, NON_BASIC_OPCODES[op], _ta)
            self.cycle += func(a)
    def operand(self, x, dereference):
        literal = False
        if x < 8: # register
            desc = REGISTERS[x]
            result = REGISTER + x
        elif 0x08 <= x <= 0x0f: # [register]
            desc = '[%s]' % REGISTERS[x - 0x08]
            result = self.ram[REGISTER + x - 0x08]
        elif 0x10 <= x <= 0x17: # [register + next word]
            word = self.next_word(int(not self.skip))
            desc = '[%s + 0x%04x]' % (REGISTERS[x - 0x10], word)
            result = self.ram[REGISTER + x - 0x10] + word
        elif x == 0x18: # POP [SP++]
            desc = 'POP'
            result = self.sp
            if not self.skip:
                self.sp = (self.sp + 1) % SIZE
        elif x == 0x19: # PEEK [SP]
            desc = 'PEEK'
            result = self.sp
        elif x == 0x1a: # PUSH [--SP]
            desc = 'PUSH'
            if not self.skip:
                self.sp = (self.sp - 1) % SIZE
            result = self.sp
        elif x == 0x1b: # SP
            desc = 'SP'
            result = SP
        elif x == 0x1c: # PC
            desc = 'PC'
            result = PC
        elif x == 0x1d: # O
            desc = 'O'
            result = O
        elif x == 0x1e: # [next word]
            word = self.next_word(int(not self.skip))
            desc = '[0x%04x]' % word
            result = word
        elif x == 0x1f: # literal (next word)
            literal = True
            word = self.next_word(int(not self.skip))
            desc = '0x%04x' % word
            result = word
        elif x >= 0x20: # literal (constant)
            literal = True
            desc = '0x%04x' % (x - 0x20)
            result = x - 0x20
        if literal and not dereference:
            self.lit = result
            result = LIT
        if dereference and not literal:
            result = self.ram[result]
        return result, desc
    # Opcode Functions
    def SET(self, a, b):
        self.ram[a] = b
        return 1
    def ADD(self, a, b):
        o, self.ram[a] = divmod(self.ram[a] + b, SIZE)
        self.o = 1 if o else 0
        return 2
    def SUB(self, a, b):
        o, self.ram[a] = divmod(self.ram[a] - b, SIZE)
        self.o = MAX_VALUE if o else 0
        return 2
    def MUL(self, a, b):
        o, self.ram[a] = divmod(self.ram[a] * b, SIZE)
        self.o = o % SIZE
        return 2
    def DIV(self, a, b):
        if b:
            self.o = ((self.ram[a] << 16) / b) % SIZE
            self.ram[a] /= b
        else:
            self.ram[a] = 0
        return 3
    def MOD(self, a, b):
        if b:
            self.ram[a] %= b
        else:
            self.ram[a] = 0
        return 3
    def SHL(self, a, b):
        o, self.ram[a] = divmod(self.ram[a] << b, SIZE)
        self.o = o % SIZE
        return 2
    def SHR(self, a, b):
        self.o = ((self.ram[a] << 16) >> b) % SIZE
        self.ram[a] >>= b
        return 2
    def AND(self, a, b):
        self.ram[a] &= b
        return 1
    def BOR(self, a, b):
        self.ram[a] |= b
        return 1
    def XOR(self, a, b):
        self.ram[a] ^= b
        return 1
    def IFE(self, a, b):
        self.skip = not (self.ram[a] == b)
        return 2 + int(self.skip)
    def IFN(self, a, b):
        self.skip = not (self.ram[a] != b)
        return 2 + int(self.skip)
    def IFG(self, a, b):
        self.skip = not (self.ram[a] > b)
        return 2 + int(self.skip)
    def IFB(self, a, b):
        self.skip = not (self.ram[a] & b)
        return 2 + int(self.skip)
    def BRK(self, a):
        self.halt = True
        return 1
    def JSR(self, a):
        self.sp = (self.sp - 1) % SIZE
        self.ram[self.sp] = self.pc
        self.pc = a
        return 2
