import time

# Constants
MAX_VALUE = 0xffff
SIZE = 0x10000
REGISTER = 0x10000
PC = 0x10008
SP = 0x10009
O = 0x1000a
REGISTERS = 'ABCXYZIJ'
CYCLES_PER_SECOND = 100000

# Basic Opcodes
SET = 0x1
ADD = 0x2
SUB = 0x3
MUL = 0x4
DIV = 0x5
MOD = 0x6
SHL = 0x7
SHR = 0x8
AND = 0x9
BOR = 0xa
XOR = 0xb
IFE = 0xc
IFN = 0xd
IFG = 0xe
IFB = 0xf

BASIC_OPCODES = {
    SET: 'SET',
    ADD: 'ADD',
    SUB: 'SUB',
    MUL: 'MUL',
    DIV: 'DIV',
    MOD: 'MOD',
    SHL: 'SHL',
    SHR: 'SHR',
    AND: 'AND',
    BOR: 'BOR',
    XOR: 'XOR',
    IFE: 'IFE',
    IFN: 'IFN',
    IFG: 'IFG',
    IFB: 'IFB',
}

# Non-Basic Opcodes
BRK = 0x0
JSR = 0x1

NON_BASIC_OPCODES = {
    BRK: 'BRK',
    JSR: 'JSR',
}

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
    # Initialization Functions
    def reset(self):
        self.ram = [0] * (SIZE + 12)
        self.skip = False
        self.halt = False
        self.cycle = 0
    def load(self, program):
        self.reset()
        for index, value in enumerate(program):
            self.ram[index] = value
    # Run Functions
    def run(self):
        while not self.halt:
            self.instruction()
    def next_word(self, cycles=0):
        word = self.ram[self.pc]
        self.pc = (self.pc + 1) % SIZE
        self.cycle += cycles
        return word
    def instruction(self):
        last_cycle = self.cycle
        word = self.next_word()
        op = word & 0x000f
        a = (word & 0x03f0) >> 4
        b = (word & 0xfc00) >> 10
        if op:
            self.basic_instruction(op, a, b)
        else:
            self.non_basic_instruction(a, b)
        cycles = self.cycle - last_cycle
        seconds = float(cycles) / CYCLES_PER_SECOND
        time.sleep(seconds)
    def basic_instruction(self, op, a, b):
        a, ta = self.operand(a, False)
        b, tb = self.operand(b, True)
        func = self.basic_opcodes[op]
        if self.skip:
            self.skip = False
        else:
            print '%04x: %s %s, %s' % (self.pc - 1, BASIC_OPCODES[op], ta, tb)
            self.cycle += func(a, b)
    def non_basic_instruction(self, op, a):
        a, ta = self.operand(a, True)
        func = self.non_basic_opcodes[op]
        if self.skip:
            self.skip = False
        else:
            print '%04x: %s %s' % (self.pc - 1, NON_BASIC_OPCODES[op], ta)
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
            word = self.next_word(1)
            desc = '[%s + 0x%04x]' % (REGISTERS[x - 0x10], word)
            result = self.ram[REGISTER + x - 0x10] + word
        elif x == 0x18: # POP [SP++]
            desc = 'POP'
            result = self.sp
            self.sp = (self.sp + 1) % SIZE
        elif x == 0x19: # PEEK [SP]
            desc = 'PEEK'
            result = self.sp
        elif x == 0x1a: # PUSH [--SP]
            desc = 'PUSH'
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
            word = self.next_word(1)
            desc = '0x%04x' % word
            result = word
        elif x == 0x1f: # literal (next word)
            literal = True
            word = self.next_word(1)
            desc = '0x%04x' % word
            result = word
        elif x >= 0x20: # literal (constant)
            literal = True
            desc = '0x%04x' % (x - 0x20)
            result = x - 0x20
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
        self.o = 1 if o else 0
        return 2
    def DIV(self, a, b):
        if b:
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
        self.o = 1 if o else 0
        return 2
    def SHR(self, a, b):
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

def main():
    program = [
        0x7c01, 0x0030, 0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d,
        0x7dc1, 0x001a, 0xa861, 0x7c01, 0x2000, 0x2161, 0x2000, 0x8463,
        0x806d, 0x7dc1, 0x000d, 0x9031, 0x7c10, 0x0018, 0x7dc1, 0x001a,
        0x9037, 0x61c1, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    ]
    emulator = Emulator()
    emulator.load(program)
    emulator.run()
    emulator.dump()

if __name__ == '__main__':
    main()
