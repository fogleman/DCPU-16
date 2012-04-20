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

# Classes
class Program(object):
    pass

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
def p_program1(t):
    'program : instruction program'
    t[0] = (t[1],) + t[2]

def p_program2(t):
    'program : instruction'
    t[0] = (t[1],)

def p_data1(t):
    'data : literal data'
    t[0] = (t[1],) + t[2]

def p_data2(t):
    'data : literal'
    t[0] = (t[1],)

def p_data3(t):
    'data : STRING'
    t[0] = (t[1],)

def p_instruction_label(t):
    'instruction : LABEL'
    t[0] = t[1]

def p_instruction_data(t):
    'instruction : DAT data'
    t[0] = t[2]

def p_instruction_basic(t):
    'instruction : basic_opcode operand operand'
    t[0] = (t[1], t[2], t[3])

def p_instruction_non_basic(t):
    'instruction : non_basic_opcode operand'
    t[0] = (t[1], t[2])

def p_operand_register(t):
    'operand : register'
    t[0] = t[1]

def p_operand_register_dereference(t):
    'operand : LBRACK register RBRACK'
    t[0] = t[2]

def p_operand_label_dereference(t):
    'operand : LBRACK ID RBRACK'
    t[0] = t[2]

def p_operand_register_literal(t):
    '''operand : LBRACK register PLUS literal RBRACK
               | LBRACK literal PLUS register RBRACK'''
    t[0] = t[1]

def p_operand_register_id(t):
    '''operand : LBRACK register PLUS ID RBRACK
               | LBRACK ID PLUS register RBRACK'''
    t[0] = t[1]

def p_operand_literal_dereference(t):
    'operand : LBRACK literal RBRACK'
    t[0] = t[2]

def p_operand_special(t):
    'operand : special'
    t[0] = t[1]

def p_operand_literal(t):
    'operand : literal'
    t[0] = t[1]

def p_operand_id(t):
    'operand : ID'
    t[0] = t[1]

def p_literal(t):
    '''literal : DECIMAL
               | HEX'''
    t[0] = t[1]

def p_basic_opcode(t):
    t[0] = t[1]
p_basic_opcode.__doc__ = ('basic_opcode : %s' % 
    '\n | '.join(sorted(BASIC_OPCODES)))

def p_non_basic_opcode(t):
    t[0] = t[1]
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

# Construct Lexer and Parser
import ply.lex as lex
import ply.yacc as yacc

# Parsing Functions
def parse(text):
    lexer = lex.lex()
    parser = yacc.yacc(debug=False, write_tables=False)
    return parser.parse(text.upper(), lexer=lexer)

def parse_file(path):
    with open(path) as fp:
        text = fp.read()
    return parse(text)

# Main
if __name__ == '__main__':
    import os
    for name in os.listdir('programs'):
        if '.dasm' not in name:
            continue
        print name
        parse_file(os.path.join('programs', name))
