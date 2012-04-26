// Constants
#define SIZE 0x10000
#define MAX_VALUE 0xffff
#define EXT_SIZE 0x1000d
#define REG_ADDR 0x10000
#define SP_ADDR 0x10008
#define PC_ADDR 0x10009
#define EX_ADDR 0x1000a
#define IA_ADDR 0x1000b
#define LT_ADDR 0x1000c

// Helper Macros
#define CONDITIONAL(opcode) ((opcode) >= 0x10 && (opcode) <= 0x17)
#define CYCLES(count) (emulator->cycle += (count))
#define RAM(address) (emulator->ram[(address)])
#define REG(index) (emulator->ram[REG_ADDR + (index)])
#define SP (emulator->ram[SP_ADDR])
#define PC (emulator->ram[PC_ADDR])
#define EX (emulator->ram[EX_ADDR])
#define IA (emulator->ram[IA_ADDR])
#define LT (emulator->ram[LT_ADDR])
#define SKIP (emulator->skip)
#define CYCLE (emulator->cycle)

// Basic Opcodes
#define SET 0x01
#define ADD 0x02
#define SUB 0x03
#define MUL 0x04
#define MLI 0x05
#define DIV 0x06
#define DVI 0x07
#define MOD 0x08
#define AND 0x09
#define BOR 0x0a
#define XOR 0x0b
#define SHR 0x0c
#define ASR 0x0d
#define SHL 0x0e
#define STI 0x0f
#define IFB 0x10
#define IFC 0x11
#define IFE 0x12
#define IFN 0x13
#define IFG 0x14
#define IFA 0x15
#define IFL 0x16
#define IFU 0x17
#define ADX 0x1a
#define SUX 0x1b

// Non Basic Opcodes
#define JSR 0x01
#define INT 0x08
#define IAG 0x09
#define IAS 0x0a
#define HWN 0x10
#define HWQ 0x11
#define HWI 0x12

// Hardware
#define N_DEVICES 3
#define LEM1802 0
#define KEYBOARD 1
#define CLOCK 2

// Boolean
#define bool unsigned int
#define true 1
#define false 0

// Emulator State
typedef struct {
    // DCPU-16
    unsigned short ram[EXT_SIZE];
    bool skip;
    unsigned long long int cycle;
    // LEM1802
    unsigned short lem1802_screen;
    unsigned short lem1802_font;
    unsigned short lem1802_palette;
    unsigned short lem1802_border;
    // KEYBOARD
    unsigned char keyboard_buffer[16];
    bool keyboard_pressed[256];
    unsigned short keyboard_pointer;
    unsigned short keyboard_message;
    // CLOCK
} Emulator;

// Emulator Functions
void reset(Emulator *emulator) {
    // DCPU-16
    for (unsigned int i = 0; i < EXT_SIZE; i++) {
        RAM(i) = 0;
    }
    SKIP = 0;
    CYCLE = 0;
    // LEM1802
    emulator->lem1802_screen = 0;
    emulator->lem1802_font = 0;
    emulator->lem1802_palette = 0;
    emulator->lem1802_border = 0;
    // KEYBOARD
    for (unsigned int i = 0; i < 16; i++) {
        emulator->keyboard_buffer[i] = 0;
    }
    for (unsigned int i = 0; i < 256; i++) {
        emulator->keyboard_pressed[i] = 0;
    }
    emulator->keyboard_pointer = 0;
    emulator->keyboard_message = 0;
}

void load(Emulator *emulator, unsigned short *program, unsigned int length) {
    if (length > SIZE) {
        length = SIZE;
    }
    for (unsigned int i = 0; i < length; i++) {
        RAM(i) = program[i];
    }
}

int operand(Emulator *emulator, unsigned char x, bool dereference) {
    int result;
    bool literal = false;
    if (x < 0x08) {
        result = REG_ADDR + x;
    }
    else if (x >= 0x08 && x <= 0x0f) {
        result = REG(x - 0x08);
    }
    else if (x >= 0x10 && x <= 0x17) {
        result = (REG(x - 0x10) + RAM(PC++)) % SIZE;
        if (!SKIP) {
            CYCLES(1);
        }
    }
    else if (x == 0x18 && dereference) {
        result = SP;
        if (!SKIP) {
            SP++;
        }
    }
    else if (x == 0x18 && !dereference) {
        if (!SKIP) {
            SP--;
        }
        result = SP;
    }
    else if (x == 0x19) {
        result = SP;
    }
    else if (x == 0x1a) {
        result = (SP + RAM(PC++)) % SIZE;
        if (!SKIP) {
            CYCLES(1);
        }
    }
    else if (x == 0x1b) {
        result = SP_ADDR;
    }
    else if (x == 0x1c) {
        result = PC_ADDR;
    }
    else if (x == 0x1d) {
        result = EX_ADDR;
    }
    else if (x == 0x1e) {
        result = RAM(PC++);
        if (!SKIP) {
            CYCLES(1);
        }
    }
    else if (x == 0x1f) {
        literal = true;
        result = RAM(PC++);
        if (!SKIP) {
            CYCLES(1);
        }
    }
    else if (x == 0x20) {
        literal = true;
        result = MAX_VALUE;
    }
    else {
        literal = true;
        result = x - 0x21;
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

int divmod(int x, int *quo) {
    int quotient = x / SIZE;
    if (x < 0 && x % SIZE) {
        quotient--;
    }
    *quo = quotient;
    return x % SIZE;
}

void basic_instruction(Emulator *emulator, unsigned char opcode, 
    unsigned char op_dst, unsigned char op_src) {
    int src = operand(emulator, op_src, true);
    int dst = operand(emulator, op_dst, false);
    int ram = RAM(dst);
    short ssrc = (short)(unsigned short)src;
    short sram = (short)(unsigned short)ram;
    int quo;
    if (SKIP) {
        if (CONDITIONAL(opcode)) {
            CYCLES(1);
        }
        else {
            SKIP = 0;
        }
        return;
    }
    switch (opcode) {
        case SET:
            RAM(dst) = src;
            CYCLES(1);
            break;
        case ADD:
            RAM(dst) = divmod(ram + src, &quo);
            EX = quo ? 1 : 0;
            CYCLES(2);
            break;
        case SUB:
            RAM(dst) = divmod(ram - src, &quo);
            EX = quo ? MAX_VALUE : 0;
            CYCLES(2);
            break;
        case MUL:
            RAM(dst) = divmod(ram * src, &quo);
            EX = quo % SIZE;
            CYCLES(2);
            break;
        case MLI:
            RAM(dst) = divmod(sram * ssrc, &quo);
            EX = quo % SIZE;
            CYCLES(2);
            break;
        case DIV:
            if (src) {
                EX = ((ram << 16) / src) % SIZE;
                RAM(dst) = (ram / src) % SIZE;
            }
            else {
                EX = 0;
                RAM(dst) = 0;
            }
            CYCLES(3);
            break;
        case DVI:
            if (src) {
                EX = ((sram << 16) / ssrc) % SIZE;
                RAM(dst) = (sram / ssrc) % SIZE;
            }
            else {
                EX = 0;
                RAM(dst) = 0;
            }
            CYCLES(3);
            break;
        case MOD:
            if (src) {
                RAM(dst) = (ram % src) % SIZE;
            }
            else {
                RAM(dst) = 0;
            }
            CYCLES(3);
            break;
        case AND:
            RAM(dst) = (ram & src) % SIZE;
            CYCLES(1);
            break;
        case BOR:
            RAM(dst) = (ram | src) % SIZE;
            CYCLES(1);
            break;
        case XOR:
            RAM(dst) = (ram ^ src) % SIZE;
            CYCLES(1);
            break;
        case SHR:
            EX = ((ram << 16) >> src) % SIZE;
            RAM(dst) = (ram >> src) % SIZE;
            CYCLES(2);
            break;
        case ASR:
            EX = ((sram << 16) >> src) % SIZE;
            RAM(dst) = (sram >> src) % SIZE;
            CYCLES(2);
            break;
        case SHL:
            EX = ((ram << src) >> 16) % SIZE;
            RAM(dst) = (ram << src) % SIZE;
            CYCLES(2);
            break;
        case STI:
            RAM(dst) = src;
            REG(6)++;
            REG(7)++;
            CYCLES(2);
            break;
        case IFB:
            SKIP = (ram & src) != 0 ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFC:
            SKIP = (ram & src) == 0 ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFE:
            SKIP = (ram == src) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFN:
            SKIP = (ram != src) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFG:
            SKIP = (ram > src) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFA:
            SKIP = (sram > ssrc) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFL:
            SKIP = (ram < src) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case IFU:
            SKIP = (sram < ssrc) ? 0 : 1;
            CYCLES(2 + SKIP);
            break;
        case ADX:
            RAM(dst) = divmod(ram + src + EX, &quo);
            EX = quo ? 1 : 0;
            CYCLES(3);
            break;
        case SUX:
            RAM(dst) = divmod(ram - src + EX, &quo);
            EX = quo ? MAX_VALUE : 0;
            CYCLES(3);
            break;
        default:
            CYCLES(1);
    }
}

void interrupt(Emulator *emulator, unsigned short message) {
    if (IA) {
        RAM(--SP) = PC;
        RAM(--SP) = REG(0);
        PC = IA;
        REG(0) = message;
    }
}

void on_lem1802(Emulator *emulator) {
    switch (REG(0)) {
        case 0: // MEM_MAP_SCREEN
            emulator->lem1802_screen = REG(1);
            break;
        case 1: // MEM_MAP_FONT
            emulator->lem1802_font = REG(1);
            break;
        case 2: // MEM_MAP_PALETTE
            emulator->lem1802_palette = REG(1);
            break;
        case 3: // SET_BORDER_COLOR
            emulator->lem1802_border = REG(1);
            break;
    }
}

void on_keyboard(Emulator *emulator) {
    switch (REG(0)) {
        case 0: // CLEAR_BUFFER
            for (unsigned int i = 0; i < 16; i++) {
                emulator->keyboard_buffer[i] = 0;
            }
            emulator->keyboard_pointer = 0;
            break;
        case 1: // GET_CHARACTER
            REG(2) = emulator->keyboard_buffer[0];
            if (REG(2)) {
                for (unsigned int i = 1; i < 16; i++) {
                    emulator->keyboard_buffer[i - 1] =
                        emulator->keyboard_buffer[i];
                }
                emulator->keyboard_buffer[15] = 0;
                emulator->keyboard_pointer--;
            }
            break;
        case 2: // IS_PRESSED
            REG(2) = REG(1) < 256 ? emulator->keyboard_pressed[REG(1)] : 0;
            break;
        case 3: // ENABLE_INTERRUPTS
            emulator->keyboard_message = REG(1);
            break;
    }
}

void on_hwq(Emulator *emulator, unsigned short index) {
    switch (index) {
        case LEM1802:
            REG(0) = 0xf615;
            REG(1) = 0x7349;
            REG(2) = 0x1802;
            REG(3) = 0x8b36;
            REG(4) = 0x1c6c;
            break;
        case KEYBOARD:
            REG(0) = 0x7406;
            REG(1) = 0x30cf;
            REG(2) = 0x0001;
            REG(3) = 0x8b36;
            REG(4) = 0x1c6c;
            break;
        case CLOCK:
            REG(0) = 0xb402;
            REG(1) = 0x12d0;
            REG(2) = 0x0001;
            REG(3) = 0x8b36;
            REG(4) = 0x1c6c;
            break;
    }
}

void on_hwi(Emulator *emulator, unsigned short index) {
    switch (index) {
        case LEM1802:
            on_lem1802(emulator);
            break;
        case KEYBOARD:
            on_keyboard(emulator);
            break;
        case CLOCK:
            break;
    }
}

void special_instruction(Emulator *emulator, unsigned char opcode, 
    unsigned char op_dst) {
    unsigned int dst = operand(emulator, op_dst, false);
    unsigned int ram = RAM(dst);
    if (SKIP) {
        SKIP = 0;
        return;
    }
    switch (opcode) {
        case JSR:
            RAM(--SP) = PC;
            PC = ram;
            CYCLES(3);
            break;
        case INT:
            if (IA) {
                interrupt(emulator, ram);
                CYCLES(4);
            }
            else {
                CYCLES(2);
            }
            break;
        case IAG:
            RAM(dst) = IA;
            CYCLES(1);
            break;
        case IAS:
            IA = ram;
            CYCLES(1);
            break;
        case HWN:
            RAM(dst) = N_DEVICES;
            CYCLES(2);
            break;
        case HWQ:
            on_hwq(emulator, ram);
            CYCLES(4);
            break;
        case HWI:
            on_hwi(emulator, ram);
            CYCLES(4);
            break;
        default:
            CYCLES(1);
    }
}

void step(Emulator *emulator) {
    unsigned short word = RAM(PC++);
    unsigned char op = word & 0x1f;
    unsigned char dst = (word >> 5) & 0x1f;
    unsigned char src = (word >> 10) & 0x3f;
    if (op) {
        basic_instruction(emulator, op, dst, src);
    }
    else {
        special_instruction(emulator, dst, src);
    }
}

void n_steps(Emulator *emulator, unsigned int steps) {
    for (unsigned int i = 0; i < steps; i++) {
        step(emulator);
    }
}

void n_cycles(Emulator *emulator, unsigned int cycles) {
    unsigned long long int cycle = CYCLE + cycles;
    while (CYCLE < cycle) {
        step(emulator);
    }
}

void on_key_down(Emulator *emulator, unsigned char key) {
    emulator->keyboard_pressed[key] = true;
    if (emulator->keyboard_message) {
        interrupt(emulator, emulator->keyboard_message);
    }
}

void on_key_up(Emulator *emulator, unsigned char key) {
    emulator->keyboard_pressed[key] = false;
    if (emulator->keyboard_message) {
        interrupt(emulator, emulator->keyboard_message);
    }
}

void on_char(Emulator *emulator, unsigned char key) {
    if (emulator->keyboard_pointer > 15) {
        return;
    }
    emulator->keyboard_buffer[emulator->keyboard_pointer++] = key;
    if (emulator->keyboard_message) {
        interrupt(emulator, emulator->keyboard_message);
    }
}
