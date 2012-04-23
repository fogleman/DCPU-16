import ply.lex as lex
import ply.yacc as yacc
import sys

# Lookups
BASIC_OPCODES = {
    'SET': 0x1,
    'ADD': 0x2,
    'SUB': 0x3,
    'MUL': 0x4,
    'DIV': 0x5,
    'MOD': 0x6,
    'SHL': 0x7,
    'SHR': 0x8,
    'AND': 0x9,
    'BOR': 0xa,
    'XOR': 0xb,
    'IFE': 0xc,
    'IFN': 0xd,
    'IFG': 0xe,
    'IFB': 0xf,
}

NON_BASIC_OPCODES = {
    'BRK': 0x0,
    'JSR': 0x1,
}

REGISTERS = {
    'A': 0x0,
    'B': 0x1,
    'C': 0x2,
    'X': 0x3,
    'Y': 0x4,
    'Z': 0x5,
    'I': 0x6,
    'J': 0x7,
}

SPECIAL = {
    'POP':  0x18,
    'PEEK': 0x19,
    'PUSH': 0x1a,
    'SP':   0x1b,
    'PC':   0x1c,
    'O':    0x1d,
}

# Reverse Lookups
REV_BASIC_OPCODES = dict((v, k) for k, v in BASIC_OPCODES.items())
REV_NON_BASIC_OPCODES = dict((v, k) for k, v in NON_BASIC_OPCODES.items())
REV_REGISTERS = dict((v, k) for k, v in REGISTERS.items())
REV_SPECIAL = dict((v, k) for k, v in SPECIAL.items())

# Classes
class Program(object):
    def __init__(self, instructions):
        self.instructions = instructions
        self.lookup = {}
        self.size = 0
        for instruction in instructions:
            instruction.offset = self.size
            if isinstance(instruction, Label):
                self.lookup[instruction.name] = instruction.offset
            self.size += instruction.size
    def assemble(self):
        result = []
        for instruction in self.instructions:
            result.extend(instruction.assemble(self.lookup))
        return result
    def pretty(self):
        lines = []
        previous = None
        for instruction in self.instructions:
            line = instruction.pretty(previous)
            data = instruction.assemble(self.lookup)
            if data and not isinstance(instruction, Data):
                pad = ' ' * (32 - len(line))
                data = ' '.join('%04x' % x for x in data)
                line = '%s%s; %s' % (line, pad, data)
            lines.append(line)
            previous = instruction
        return '\n'.join(lines)
    def disassembly(self):
        result = []
        for instruction in self.instructions:
            if isinstance(instruction, Label):
                continue
            result.append(instruction)
        return result

class Data(object):
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.offset = None
        self.conditional = False
    def assemble(self, lookup):
        return [lookup.get(x, x) for x in self.data]
    def pretty(self, previous):
        data = ', '.join('"%s"' % x if isinstance(x, str) else pretty_value(x)
            for x in self.data)
        return '    DAT %s' % data

class Label(object):
    def __init__(self, name):
        self.name = name
        self.size = 0
        self.offset = None
        self.conditional = False
    def assemble(self, lookup):
        return []
    def pretty(self, previous):
        return ':%s' % self.name.lower()

class BasicInstruction(object):
    def __init__(self, opcode, arg1, arg2):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        value = self.opcode
        value |= (self.arg1.value & 0x3f) << 4
        value |= (self.arg2.value & 0x3f) << 10
        self.value = value
        self.size = 1 + arg1.size + arg2.size
        self.offset = None
        self.conditional = 0xc <= self.opcode <= 0xf
    def assemble(self, lookup):
        result = [self.value]
        result.extend(self.arg1.assemble(lookup))
        result.extend(self.arg2.assemble(lookup))
        return result
    def pretty(self, previous):
        a = REV_BASIC_OPCODES[self.opcode]
        b = self.arg1.pretty()
        c = self.arg2.pretty()
        p = '    '
        if previous and previous.conditional:
            p *= 2
        return '%s%s %s, %s' % (p, a, b, c)

class NonBasicInstruction(object):
    def __init__(self, opcode, arg):
        self.opcode = opcode
        self.arg = arg
        value = 0
        value |= (self.opcode & 0x3f) << 4
        value |= (self.arg.value & 0x3f) << 10
        self.value = value
        self.size = 1 + arg.size
        self.offset = None
        self.conditional = False
    def assemble(self, lookup):
        result = [self.value]
        result.extend(self.arg.assemble(lookup))
        return result
    def pretty(self, previous):
        a = REV_NON_BASIC_OPCODES[self.opcode]
        b = self.arg.pretty()
        return '    %s %s' % (a, b)

class Operand(object):
    def __init__(self, value, word=None):
        self.value = value
        self.word = word
        self.size = int(word is not None)
    def assemble(self, lookup):
        return [] if self.word is None else [lookup.get(self.word, self.word)]
    def pretty(self):
        x = self.value
        word = self.word
        if isinstance(word, int):
            word = pretty_value(word)
        elif isinstance(word, str):
            word = word.lower()
        if x in REV_REGISTERS:
            return REV_REGISTERS[x]
        elif x - 0x08 in REV_REGISTERS:
            return '[%s]' % REV_REGISTERS[x - 0x08]
        elif x - 0x10 in REV_REGISTERS:
            return '[%s + %s]' % (REV_REGISTERS[x - 0x10], word)
        elif x in REV_SPECIAL:
            return REV_SPECIAL[x]
        elif x == 0x1e:
            return '[%s]' % word
        elif x == 0x1f:
            return '%s' % word
        elif x >= 0x20:
            return pretty_value(x - 0x20)

# Lexer Rules
reserved = (
    BASIC_OPCODES.keys() + 
    NON_BASIC_OPCODES.keys() + 
    REGISTERS.keys() + 
    SPECIAL.keys() +
    ['DAT']
)

tokens = [
    'LBRACK',
    'RBRACK',
    'PLUS',
    'LABEL',
    'ID',
    'DECIMAL',
    'HEX',
    'STRING',
] + reserved

t_ignore = ' \t\r,'
t_ignore_COMMENT = r';.*'

t_LBRACK = r'\['
t_RBRACK = r'\]'
t_PLUS = r'\+'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_STRING(t):
    r'"[^"]*"'
    t.value = tuple(ord(x) for x in t.value[1:-1])
    return t

def t_HEX(t):
    r'0X[a-fA-F0-9]+'
    t.value = int(t.value, 16)    
    return t

def t_DECIMAL(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_LABEL(t):
    r':[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value[1:]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value in reserved:
        t.type = t.value
    else:
        t.type = 'ID'
    return t

def t_error(t):
    raise Exception(t)

# Parser Rules
def p_program(t):
    'program : instructions'
    t[0] = Program(t[1])

def p_instructions1(t):
    'instructions : instruction instructions'
    t[0] = (t[1],) + t[2]

def p_instructions2(t):
    'instructions : instruction'
    t[0] = (t[1],)

def p_data1(t):
    'data : literal data'
    arg = t[1] if isinstance(t[1], tuple) else (t[1],)
    t[0] = arg + t[2]

def p_data2(t):
    'data : literal'
    arg = t[1] if isinstance(t[1], tuple) else (t[1],)
    t[0] = arg

def p_instruction_data(t):
    'instruction : DAT data'
    t[0] = Data(t[2])

def p_instruction_label(t):
    'instruction : LABEL'
    t[0] = Label(t[1])

def p_instruction_basic(t):
    'instruction : basic_opcode operand operand'
    t[0] = BasicInstruction(t[1], t[2], t[3])

def p_instruction_non_basic(t):
    'instruction : non_basic_opcode operand'
    t[0] = NonBasicInstruction(t[1], t[2])

def p_operand_register(t):
    'operand : register'
    t[0] = Operand(REGISTERS[t[1]])

def p_operand_register_dereference(t):
    'operand : LBRACK register RBRACK'
    t[0] = Operand(REGISTERS[t[2]] + 0x08)

def p_operand_register_literal1(t):
    'operand : LBRACK register PLUS literal RBRACK'
    t[0] = Operand(REGISTERS[t[2]] + 0x10, t[4])

def p_operand_register_literal2(t):
    'operand : LBRACK literal PLUS register RBRACK'
    t[0] = Operand(REGISTERS[t[4]] + 0x10, t[2])

def p_operand_special(t):
    'operand : special'
    t[0] = Operand(SPECIAL[t[1]])

def p_operand_literal_dereference(t):
    'operand : LBRACK literal RBRACK'
    t[0] = Operand(0x1e, t[2])

def p_operand_literal(t):
    'operand : literal'
    if t[1] < 0x20:
        t[0] = Operand(t[1] + 0x20)
    else:
        t[0] = Operand(0x1f, t[1])

def p_literal(t):
    '''literal : DECIMAL
               | HEX
               | ID
               | STRING'''
    t[0] = t[1]

def p_basic_opcode(t):
    t[0] = BASIC_OPCODES[t[1]]
p_basic_opcode.__doc__ = ('basic_opcode : %s' % 
    '\n | '.join(sorted(BASIC_OPCODES)))

def p_non_basic_opcode(t):
    t[0] = NON_BASIC_OPCODES[t[1]]
p_non_basic_opcode.__doc__ = ('non_basic_opcode : %s' % 
    '\n | '.join(sorted(NON_BASIC_OPCODES)))

def p_register(t):
    t[0] = t[1]
p_register.__doc__ = ('register : %s' % 
    '\n | '.join(sorted(REGISTERS)))

def p_special(t):
    t[0] = t[1]
p_special.__doc__ = ('special : %s' % 
    '\n | '.join(sorted(SPECIAL)))

def p_error(t):
    raise Exception(t)

# Parsing Functions
def parse(text):
    lexer = lex.lex()
    parser = yacc.yacc(debug=False, write_tables=False)
    return parser.parse(text.upper(), lexer=lexer)

def parse_file(path):
    with open(path) as fp:
        text = fp.read()
    return parse(text)

def assemble(text):
    program = parse(text)
    return program.assemble()

def assemble_file(path):
    with open(path) as fp:
        text = fp.read()
    return assemble(text)

def pretty(text):
    program = parse(text)
    return program.pretty()

def pretty_file(path):
    with open(path) as fp:
        text = fp.read()
    return pretty(text)

def pretty_value(x):
    return '%d' % x if x <= 0xff else '0x%04x' % x

# Main
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        print pretty_file(args[0])
    else:
        print 'Usage: python assembler.py input.dasm'
