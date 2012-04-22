// Constants
#define SIZE 0x10000
#define MAX_VALUE 0xffff
#define EXT_SIZE 0x1000c
#define REG_ADDR 0x10000
#define SP_ADDR 0x10008
#define PC_ADDR 0x10009
#define OV_ADDR 0x1000a
#define LT_ADDR 0x1000b

// Helper Macros
#define CYCLES(count) (emulator->cycle += (count))
#define RAM(address) (emulator->ram[(address)])
#define REG(index) (emulator->ram[REG_ADDR + (index)])
#define SP (emulator->ram[SP_ADDR])
#define PC (emulator->ram[PC_ADDR])
#define OV (emulator->ram[OV_ADDR])
#define LT (emulator->ram[LT_ADDR])
#define SKIP (emulator->skip)
#define HALT (emulator->halt)
#define CYCLE (emulator->cycle)

// Basic Opcodes
#define SET 0x1
#define ADD 0x2
#define SUB 0x3
#define MUL 0x4
#define DIV 0x5
#define MOD 0x6
#define SHL 0x7
#define SHR 0x8
#define AND 0x9
#define BOR 0xa
#define XOR 0xb
#define IFE 0xc
#define IFN 0xd
#define IFG 0xe
#define IFB 0xf

// Non Basic Opcodes
#define BRK 0x0
#define JSR 0x1

// Default Font Glyphs
unsigned short GLYPHS[] = {
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
};

// Emulator State
typedef struct {
    unsigned short *ram;
    unsigned int skip;
    unsigned int halt;
    unsigned int cycle;
} Emulator;

// Emulator Functions
void reset(Emulator *emulator) {
    SKIP = 0;
    HALT = 0;
    CYCLE = 0;
    for (unsigned int i = 0; i < EXT_SIZE; i++) {
        RAM(i) = 0;
    }
    for (unsigned int i = 0; i < 256; i++) {
        RAM(0x8180 + i) = GLYPHS[i];
    }
}

void load(Emulator *emulator, unsigned short *program, unsigned int length) {
    reset(emulator);
    for (unsigned int i = 0; i < length; i++) {
        RAM(i) = program[i];
    }
}

unsigned int operand(Emulator *emulator, unsigned short x, 
    unsigned int dereference) {
    unsigned int result;
    unsigned int literal = 0;
    
    switch (x) {
        case 0:
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
           result = REG_ADDR + x;
           break;
           
        case 8:
        case 9:
        case 10:
        case 11:
        case 12:
        case 13:
        case 14:
        case 15:
            result = REG(x - 0x08);
            break;

        case 16:
        case 17:
        case 18:
        case 19:
        case 20:
        case 21:
        case 22:
        case 23:
            result = REG(x - 0x10) + RAM(PC++);
            if (!SKIP) {
               CYCLES(1);
            }
            break;
            
        case 24:
            result = SP;
            if (!SKIP) {
                SP++;
            }
            break;

        case 25:
            result = SP;
            break;
        
        case 26:
            if (!SKIP) {
                SP--;
            }
            result = SP;
            break;
    
        case 27:
            result = SP_ADDR;
            break;
            
        case 28:
            result = PC_ADDR;
            break;

        case 29:
            result = OV_ADDR;
            break;

        case 30:
            result = RAM(PC++);
            if (!SKIP) {
                CYCLES(1);
            }
            break;
   
        case 31:
            literal = 1;
            result = RAM(PC++);
            if (!SKIP) {
                CYCLES(1);
            }
            break;
            
        default:
            literal = 1;
            result = x - 0x20;
            break;
    }
    
    if (literal && !dereference) {
        LT = result;
        result = LT_ADDR;
    }
    if (dereference && !literal) {
        result = RAM(result);
    }
    return result;
}

unsigned short divmod(unsigned int x, unsigned short *quo) {
    *quo = x / SIZE;
    return x % SIZE;
}

void basic_instruction(Emulator *emulator, unsigned short opcode, 
    unsigned short op_a, unsigned short op_b) {
    unsigned int a = operand(emulator, op_a, 0);
    unsigned int b = operand(emulator, op_b, 1);
    unsigned int ram = RAM(a);
    unsigned short quo;
    if (SKIP) {
        SKIP = 0;
        return;
    }
    switch (opcode) {
        case SET:
            RAM(a) = b;
            CYCLES(1);
            break;
        case ADD:
            RAM(a) = divmod(ram + b, &quo);
            OV = quo ? 1 : 0;
            CYCLES(2);
            break;
        case SUB:
            RAM(a) = divmod(ram - b, &quo);
            OV = quo ? MAX_VALUE : 0;
            CYCLES(2);
            break;
        case MUL:
            RAM(a) = divmod(ram * b, &quo);
            OV = quo % SIZE;
            CYCLES(2);
            break;
        case DIV:
            if (b) {
                OV = ((ram << 16) / b) % SIZE;
                RAM(a) /= b;
            }
            else {
                OV = 0;
                RAM(a) = 0;
            }
            CYCLES(3);
            break;
        case MOD:
            if (b) {
                RAM(a) %= b;
            }
            else {
                RAM(a) = 0;
            }
            CYCLES(3);
            break;
        case SHL:
            RAM(a) = divmod(ram << b, &quo);
            OV = quo % SIZE;
            CYCLES(2);
            break;
        case SHR:
            OV = ((ram << 16) >> b) % SIZE;
            RAM(a) >>= b;
            CYCLES(2);
            break;
        case AND:
            RAM(a) &= b;
            CYCLES(1);
            break;
        case BOR:
            RAM(a) |= b;
            CYCLES(1);
            break;
        case XOR:
            RAM(a) ^= b;
            CYCLES(1);
            break;
        case IFE:
            SKIP = (ram == b) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFN:
            SKIP = (ram != b) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFG:
            SKIP = (ram > b) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFB:
            SKIP = (ram & b) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
    }
}

void non_basic_instruction(Emulator *emulator, unsigned short opcode, 
    unsigned short op_a) {
    unsigned int a = operand(emulator, op_a, 1);
    if (SKIP) {
        SKIP = 0;
        return;
    }
    switch (opcode) {
        case BRK:
            HALT = 1;
            CYCLES(1);
            break;
        case JSR:
            RAM(--SP) = PC;
            PC = a;
            CYCLES(2);
            break;
    }
}

void step(Emulator *emulator) {
    unsigned short pc = PC;
    unsigned short word = RAM(PC++);
    unsigned short op = word & 0x000f;
    unsigned short a = (word & 0x03f0) >> 4;
    unsigned short b = (word & 0xfc00) >> 10;
    if (op) {
        basic_instruction(emulator, op, a, b);
    }
    else {
        non_basic_instruction(emulator, a, b);
    }
}

void n_cycles(Emulator *emulator, unsigned int cycles) {
    unsigned int cycle = CYCLE + cycles;
    while (CYCLE < cycle) {
        step(emulator);
    }
}
