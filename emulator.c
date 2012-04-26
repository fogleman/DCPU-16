// Constants
#define SIZE 0x10000
#define MAX_VALUE 0xffff
#define EXT_SIZE 0x10010
#define REG_ADDR 0x10000
#define SP_ADDR 0x10008
#define PC_ADDR 0x10009
#define EX_ADDR 0x1000a
#define IA_ADDR 0x1000b
#define LT_ADDR 0x1000c

// Helper Macros
#define NEXT_TICK (emulator->cycle + 100000 * emulator->clock_rate / 60)
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
#define MDI 0x09
#define AND 0x0a
#define BOR 0x0b
#define XOR 0x0c
#define SHR 0x0d
#define ASR 0x0e
#define SHL 0x0f
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
#define STI 0x1e
#define STD 0x1f

// Non Basic Opcodes
#define JSR 0x01
#define INT 0x08
#define IAG 0x09
#define IAS 0x0a
#define IAP 0x0b
#define IAQ 0x0c
#define HWN 0x10
#define HWQ 0x11
#define HWI 0x12

// Hardware
#define N_DEVICES 3
#define LEM1802 0
#define KEYBOARD 1
#define CLOCK 2

// Default Font
unsigned short LEM1802_FONT[] = {
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

// Default Palette
unsigned short LEM1802_PALETTE[] = {
    0x0000, 0x000a, 0x00a0, 0x00aa, 0x0a00, 0x0a0a, 0x0a50, 0x0aaa,
    0x0555, 0x055f, 0x05f5, 0x05ff, 0x0f55, 0x0f5f, 0x0ff5, 0x0fff,
};

// Emulator State
typedef struct {
    // DCPU-16
    unsigned short ram[EXT_SIZE];
    unsigned int skip;
    unsigned long long int cycle;
    // LEM1802
    unsigned short lem1802_screen;
    unsigned short lem1802_font;
    unsigned short lem1802_palette;
    unsigned short lem1802_border;
    // KEYBOARD
    unsigned char keyboard_buffer[16];
    unsigned char keyboard_pressed[256];
    unsigned short keyboard_pointer;
    unsigned short keyboard_message;
    // CLOCK
    unsigned long long int clock_cycle;
    unsigned short clock_rate;
    unsigned short clock_ticks;
    unsigned short clock_message;
    unsigned short dummy;
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
    // CLOCK
    emulator->clock_cycle = 0;
    emulator->clock_rate = 0;
    emulator->clock_ticks = 0;
    emulator->clock_message = 0;
}

void load(Emulator *emulator, unsigned short *program, unsigned int length) {
    if (length > SIZE) {
        length = SIZE;
    }
    for (unsigned int i = 0; i < length; i++) {
        RAM(i) = program[i];
    }
}

int operand(Emulator *emulator, unsigned char x, unsigned char dereference) {
    int result;
    unsigned char literal = 0;
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
        literal = 1;
        result = RAM(PC++);
        if (!SKIP) {
            CYCLES(1);
        }
    }
    else if (x == 0x20) {
        literal = 1;
        result = MAX_VALUE;
    }
    else {
        literal = 1;
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
    int src = operand(emulator, op_src, 1);
    int dst = operand(emulator, op_dst, 0);
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
        case MDI:
            if (src) {
                RAM(dst) = (sram % ssrc) % SIZE;
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
        case STI:
            RAM(dst) = src;
            REG(6)++;
            REG(7)++;
            CYCLES(2);
            break;
        case STD:
            RAM(dst) = src;
            REG(6)--;
            REG(7)--;
            CYCLES(2);
            break;
        default:
            CYCLES(1);
            break;
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
    unsigned short address;
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
        case 4: // DUMP_FONT
            address = REG(1);
            for (unsigned int i = 0; i < 256; i++) {
                RAM(address++) = LEM1802_FONT[i];
            }
            CYCLES(256);
            break;
        case 5: // DUMP_PALETTE
            address = REG(1);
            for (unsigned int i = 0; i < 16; i++) {
                RAM(address++) = LEM1802_PALETTE[i];
            }
            CYCLES(16);
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

void on_clock(Emulator *emulator) {
    switch (REG(0)) {
        case 0: // SET_RATE
            emulator->clock_cycle = REG(1) ? NEXT_TICK : 0;
            emulator->clock_rate = REG(1);
            emulator->clock_ticks = 0;
            break;
        case 1: // GET_TICKS
            REG(2) = emulator->clock_ticks;
            break;
        case 2: // ENABLE_INTERRUPTS
            emulator->clock_message = REG(1);
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
    int dst = operand(emulator, op_dst, 0);
    int ram = RAM(dst);
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
        case IAP:
            if (IA) {
                RAM(--SP) = IA;
                IA = REG(0);
            }
            CYCLES(3);
            break;
        case IAQ:
            CYCLES(2);
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
            break;
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
    if (emulator->clock_rate) {
        if (emulator->cycle >= emulator->clock_cycle) {
            emulator->clock_ticks++;
            emulator->clock_cycle = NEXT_TICK;
            if (emulator->clock_message) {
                interrupt(emulator, emulator->clock_message);
            }
        }
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
    emulator->keyboard_pressed[key] = 1;
    if (emulator->keyboard_message) {
        interrupt(emulator, emulator->keyboard_message);
    }
}

void on_key_up(Emulator *emulator, unsigned char key) {
    emulator->keyboard_pressed[key] = 0;
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
