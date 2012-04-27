import ply.lex as lex
import ply.yacc as yacc
import sys

# Constants
SIZE = 0x10000

# Lookups
BASIC_OPCODES = {
    'SET': 0x01,
    'ADD': 0x02,
    'SUB': 0x03,
    'MUL': 0x04,
    'MLI': 0x05,
    'DIV': 0x06,
    'DVI': 0x07,
    'MOD': 0x08,
    'MDI': 0x09,
    'AND': 0x0a,
    'BOR': 0x0b,
    'XOR': 0x0c,
    'SHR': 0x0d,
    'ASR': 0x0e,
    'SHL': 0x0f,
    'IFB': 0x10,
    'IFC': 0x11,
    'IFE': 0x12,
    'IFN': 0x13,
    'IFG': 0x14,
    'IFA': 0x15,
    'IFL': 0x16,
    'IFU': 0x17,
    'ADX': 0x1a,
    'SUX': 0x1b,
    'STI': 0x1e,
    'STD': 0x1f,
}

SPECIAL_OPCODES = {
    'JSR': 0x01,
    'BRK': 0x02,
    'INT': 0x08,
    'IAG': 0x09,
    'IAS': 0x0a,
    'RFI': 0x0b,
    'IAQ': 0x0c,
    'HWN': 0x10,
    'HWQ': 0x11,
    'HWI': 0x12,
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

DST_CODES = {
    'PUSH': 0x18,
    'PEEK': 0x19,
    'SP': 0x1b,
    'PC': 0x1c,
    'EX': 0x1d,
}

SRC_CODES = {
    'POP': 0x18,
    'PEEK': 0x19,
    'SP': 0x1b,
    'PC': 0x1c,
    'EX': 0x1d,
}

# Reverse Lookups
REV_BASIC_OPCODES = dict((v, k) for k, v in BASIC_OPCODES.items())
REV_SPECIAL_OPCODES = dict((v, k) for k, v in SPECIAL_OPCODES.items())
REV_REGISTERS = dict((v, k) for k, v in REGISTERS.items())
REV_DST_CODES = dict((v, k) for k, v in DST_CODES.items())
REV_SRC_CODES = dict((v, k) for k, v in SRC_CODES.items())

# Classes
class Program(object):
    def __init__(self, instructions):
        self.instructions = instructions
        self.text = None
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
        return ':%s' % self.name

class BasicInstruction(object):
    def __init__(self, op, dst, src):
        self.op = op
        self.dst = dst
        self.src = src
        value = self.op
        value |= (self.dst.value & 0x1f) << 5
        value |= (self.src.value & 0x3f) << 10
        self.value = value
        self.size = 1 + dst.size + src.size
        self.offset = None
        self.conditional = 0x10 <= self.op <= 0x17
    def assemble(self, lookup):
        result = [self.value]
        result.extend(self.src.assemble(lookup))
        result.extend(self.dst.assemble(lookup))
        return result
    def pretty(self, previous):
        op = REV_BASIC_OPCODES[self.op]
        dst = self.dst.pretty()
        src = self.src.pretty()
        p = '    '
        if previous and previous.conditional:
            p *= 2
        return '%s%s %s, %s' % (p, op, dst, src)

class SpecialInstruction(object):
    def __init__(self, op, src):
        self.op = op
        self.src = src
        value = 0
        value |= (self.op & 0x1f) << 5
        value |= (self.src.value & 0x3f) << 10
        self.value = value
        self.size = 1 + src.size
        self.offset = None
        self.conditional = False
    def assemble(self, lookup):
        result = [self.value]
        result.extend(self.src.assemble(lookup))
        return result
    def pretty(self, previous):
        op = REV_SPECIAL_OPCODES[self.op]
        src = self.src.pretty() if op != 'BRK' else ''
        return ('    %s %s' % (op, src)).rstrip()

class DstOperand(object):
    def __init__(self, value, word=None):
        self.value = value
        self.word = word
        self.size = int(word is not None)
    def assemble(self, lookup):
        return [] if self.word is None else [lookup.get(self.word, self.word)]
    def pretty(self):
        return pretty_operand(self.value, self.word, REV_DST_CODES)

class SrcOperand(object):
    def __init__(self, value, word=None):
        self.value = value
        self.word = word
        self.size = int(word is not None)
    def assemble(self, lookup):
        return [] if self.word is None else [lookup.get(self.word, self.word)]
    def pretty(self):
        return pretty_operand(self.value, self.word, REV_SRC_CODES)

# Lexer Rules
reserved = set(
    BASIC_OPCODES.keys() +
    SPECIAL_OPCODES.keys() +
    REGISTERS.keys() +
    DST_CODES.keys() +
    SRC_CODES.keys() +
    ['PICK', 'DAT']
)

tokens = [
    'LBRACK',
    'RBRACK',
    'PLUS',
    'LABEL',
    'ID',
    'DECIMAL',
    'HEX',
    'OCT',
    'STRING',
    'CHAR',
    'INC',
    'DEC',
] + list(reserved)

t_ignore = ' \t\r,'
t_ignore_COMMENT = r';.*'

t_INC = r'\+\+'
t_DEC = r'\-\-'
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

def t_CHAR(t):
    r"'[^']'"
    t.value = ord(t.value[1])
    return t

def t_HEX(t):
    r'\-?0x[a-fA-F0-9]+'
    t.value = int(t.value, 16) % SIZE
    return t

def t_OCT(t):
    r'\-?0\d+'
    t.value = int(t.value, 8) % SIZE
    return t

def t_DECIMAL(t):
    r'\-?\d+'
    t.value = int(t.value) % SIZE
    return t

def t_LABEL(t):
    r':[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = t.value[1:]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    upper = t.value.upper()
    if upper in reserved:
        t.type = upper
        t.value = upper
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

def p_instruction_break(t):
    'instruction : BRK'
    t[0] = SpecialInstruction(SPECIAL_OPCODES['BRK'], SrcOperand(0))

def p_instruction_basic(t):
    'instruction : basic_opcode dst_operand src_operand'
    t[0] = BasicInstruction(t[1], t[2], t[3])

def p_instruction_special(t):
    'instruction : special_opcode src_operand'
    t[0] = SpecialInstruction(t[1], t[2])

def p_dst_operand_register(t):
    'dst_operand : register'
    t[0] = DstOperand(REGISTERS[t[1]])

def p_dst_operand_register_dereference(t):
    'dst_operand : LBRACK register RBRACK'
    t[0] = DstOperand(REGISTERS[t[2]] + 0x08)

def p_dst_operand_register_literal_dereference1(t):
    'dst_operand : LBRACK register PLUS literal RBRACK'
    t[0] = DstOperand(REGISTERS[t[2]] + 0x10, t[4])

def p_dst_operand_register_literal_dereference2(t):
    'dst_operand : LBRACK literal PLUS register RBRACK'
    t[0] = DstOperand(REGISTERS[t[4]] + 0x10, t[2])

def p_dst_operand_pick1(t):
    'dst_operand : LBRACK SP PLUS literal RBRACK'
    t[0] = DstOperand(0x1a, t[4])

def p_dst_operand_pick2(t):
    'dst_operand : LBRACK literal PLUS SP RBRACK'
    t[0] = DstOperand(0x1a, t[2])

def p_dst_operand_pick3(t):
    'dst_operand : PICK literal'
    t[0] = DstOperand(0x1a, t[2])

def p_dst_operand_code(t):
    'dst_operand : dst_code'
    t[0] = DstOperand(DST_CODES[t[1]])

def p_dst_operand_push(t):
    'dst_operand : LBRACK DEC SP RBRACK'
    t[0] = DstOperand(0x18)

def p_dst_operand_peek(t):
    'dst_operand : LBRACK SP RBRACK'
    t[0] = DstOperand(0x19)

def p_dst_operand_literal_dereference(t):
    'dst_operand : LBRACK literal RBRACK'
    t[0] = DstOperand(0x1e, t[2])

def p_dst_operand_literal(t):
    'dst_operand : literal'
    t[0] = DstOperand(0x1f, t[1])

def p_src_operand_register(t):
    'src_operand : register'
    t[0] = SrcOperand(REGISTERS[t[1]])

def p_src_operand_register_dereference(t):
    'src_operand : LBRACK register RBRACK'
    t[0] = SrcOperand(REGISTERS[t[2]] + 0x08)

def p_src_operand_register_literal_dereference1(t):
    'src_operand : LBRACK register PLUS literal RBRACK'
    t[0] = SrcOperand(REGISTERS[t[2]] + 0x10, t[4])

def p_src_operand_register_literal_dereference2(t):
    'src_operand : LBRACK literal PLUS register RBRACK'
    t[0] = SrcOperand(REGISTERS[t[4]] + 0x10, t[2])

def p_src_operand_pick1(t):
    'src_operand : LBRACK SP PLUS literal RBRACK'
    t[0] = SrcOperand(0x1a, t[4])

def p_src_operand_pick2(t):
    'src_operand : LBRACK literal PLUS SP RBRACK'
    t[0] = SrcOperand(0x1a, t[2])

def p_src_operand_pick3(t):
    'src_operand : PICK literal'
    t[0] = SrcOperand(0x1a, t[2])

def p_src_operand_code(t):
    'src_operand : src_code'
    t[0] = SrcOperand(SRC_CODES[t[1]])

def p_src_operand_pop(t):
    'src_operand : LBRACK SP INC RBRACK'
    t[0] = SrcOperand(0x18)

def p_src_operand_peek(t):
    'src_operand : LBRACK SP RBRACK'
    t[0] = SrcOperand(0x19)

def p_src_operand_literal_dereference(t):
    'src_operand : LBRACK literal RBRACK'
    t[0] = SrcOperand(0x1e, t[2])

def p_src_operand_literal(t):
    'src_operand : literal'
    if t[1] == 0xffff:
        t[0] = SrcOperand(0x20)
    elif t[1] <= 0x1e:
        t[0] = SrcOperand(0x21 + t[1])
    else:
        t[0] = SrcOperand(0x1f, t[1])

def p_literal(t):
    '''literal : DECIMAL
               | HEX
               | OCT
               | ID
               | STRING
               | CHAR'''
    t[0] = t[1]

def p_basic_opcode(t):
    t[0] = BASIC_OPCODES[t[1]]
p_basic_opcode.__doc__ = ('basic_opcode : %s' % 
    '\n | '.join(sorted(BASIC_OPCODES)))

def p_special_opcode(t):
    t[0] = SPECIAL_OPCODES[t[1]]
p_special_opcode.__doc__ = ('special_opcode : %s' % 
    '\n | '.join(sorted(SPECIAL_OPCODES)))

def p_register(t):
    t[0] = t[1]
p_register.__doc__ = ('register : %s' % 
    '\n | '.join(sorted(REGISTERS)))

def p_dst_code(t):
    t[0] = t[1]
p_dst_code.__doc__ = ('dst_code : %s' % 
    '\n | '.join(sorted(DST_CODES)))

def p_src_code(t):
    t[0] = t[1]
p_src_code.__doc__ = ('src_code : %s' % 
    '\n | '.join(sorted(SRC_CODES)))

def p_error(t):
    raise Exception(t)

# Parsing Functions
def open_file(path):
    extensions = ['.dasm', '.dasm16']
    if any(ext in path for ext in extensions):
        return parse_file(path)
    else:
        return disassemble_file(path)

def parse(text):
    lexer = lex.lex()
    parser = yacc.yacc(debug=False, write_tables=False)
    program = parser.parse(text, lexer=lexer)
    program.text = text
    return program

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

def pretty_operand(x, word, codes):
    if isinstance(word, int):
        word = pretty_value(word)
    if x in REV_REGISTERS:
        return REV_REGISTERS[x]
    elif x - 0x08 in REV_REGISTERS:
        return '[%s]' % REV_REGISTERS[x - 0x08]
    elif x - 0x10 in REV_REGISTERS:
        return '[%s + %s]' % (REV_REGISTERS[x - 0x10], word)
    elif x in codes:
        return codes[x]
    elif x == 0x1a:
        return 'PICK %s' % word
    elif x == 0x1e:
        return '[%s]' % word
    elif x == 0x1f:
        return '%s' % word
    elif x == 0x20:
        return pretty_value(0xffff)
    elif x >= 0x21:
        return pretty_value(x - 0x21)

# Disassembler Functions
def disassemble(words):
    def next_word():
        return words.pop() if words else 0
    instructions = []
    use_next_word = set(range(0x10, 0x18) + [0x1a, 0x1e, 0x1f])
    words = list(reversed(words))
    while words:
        word = next_word()
        op = word & 0x1f
        dst = (word >> 5) & 0x1f
        src = (word >> 10) & 0x3f
        if op != 0 and op in REV_BASIC_OPCODES:
            dst = DstOperand(dst, next_word()
                if dst in use_next_word else None)
            src = SrcOperand(src, next_word()
                if src in use_next_word else None)
            instruction = BasicInstruction(op, dst, src)
            instructions.append(instruction)
        elif op == 0 and dst in REV_SPECIAL_OPCODES:
            src = SrcOperand(src, next_word()
                if src in use_next_word else None)
            instruction = SpecialInstruction(dst, src)
            instructions.append(instruction)
        else:
            instruction = Data([word])
            instructions.append(instruction)
    program = Program(instructions)
    program.text = program.pretty()
    return program

def disassemble_file(path):
    with open(path, 'rb') as fp:
        data = fp.read()
    words = [(ord(a) << 8) | ord(b) for a, b in zip(data[::2], data[1::2])]
    return disassemble(words)

# Main
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        print pretty_file(args[0])
    else:
        print 'Usage: python assembler.py input.dasm'
