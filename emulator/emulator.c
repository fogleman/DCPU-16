#include "common.h"
#include "emulator.h"
#include "lem.h"
#include "keyboard.h"
#include "clock.h"

// Emulator Functions
void reset(Emulator *emulator) {
    // DCPU-16
    for (unsigned int i = 0; i < EXT_SIZE; i++) {
        RAM(i) = 0;
    }
    SKIP = 0;
    HALT = 0;
    CYCLE = 0;
    for (unsigned int i = 0; i < 256; i++) {
        emulator->interrupt_buffer[i] = 0;
    }
    emulator->interrupt_index = 0;
    emulator->interrupt_queueing = 0;
    // LEM
    emulator->lem_screen = 0;
    emulator->lem_font = 0;
    emulator->lem_palette = 0;
    emulator->lem_border = 0;
    // KEYBOARD
    for (unsigned int i = 0; i < 16; i++) {
        emulator->keyboard_buffer[i] = 0;
    }
    for (unsigned int i = 0; i < 256; i++) {
        emulator->keyboard_pressed[i] = 0;
    }
    emulator->keyboard_index = 0;
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

void interrupt(Emulator *emulator, unsigned short message) {
    if (emulator->interrupt_index < 256) {
        emulator->interrupt_buffer[emulator->interrupt_index++] = message;
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
    int mod;
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
            mod = divmod(ram + src, &quo);
            EX = quo ? 1 : 0;
            RAM(dst) = mod;
            CYCLES(2);
            break;
        case SUB:
            mod = divmod(ram - src, &quo);
            EX = quo ? MAX_VALUE : 0;
            RAM(dst) = mod;
            CYCLES(2);
            break;
        case MUL:
            mod = divmod(ram * src, &quo);
            EX = quo % SIZE;
            RAM(dst) = mod;
            CYCLES(2);
            break;
        case MLI:
            mod = divmod(sram * ssrc, &quo);
            EX = quo % SIZE;
            RAM(dst) = mod;
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
            CYCLES(1);
            break;
        case ASR:
            EX = ((sram << 16) >> src) % SIZE;
            RAM(dst) = (sram >> src) % SIZE;
            CYCLES(1);
            break;
        case SHL:
            EX = ((ram << src) >> 16) % SIZE;
            RAM(dst) = (ram << src) % SIZE;
            CYCLES(1);
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
            mod = divmod(ram + src + EX, &quo);
            EX = quo ? 1 : 0;
            RAM(dst) = mod;
            CYCLES(3);
            break;
        case SUX:
            mod = divmod(ram - src + EX, &quo);
            EX = quo ? MAX_VALUE : 0;
            RAM(dst) = mod;
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

void on_hwq(Emulator *emulator, unsigned short index) {
    switch (index) {
        case LEM:
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
        case LEM:
            on_lem(emulator);
            break;
        case KEYBOARD:
            on_keyboard(emulator);
            break;
        case CLOCK:
            on_clock(emulator);
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
        case BRK:
            HALT = 1;
            CYCLES(1);
            break;
        case INT:
            interrupt(emulator, ram);
            CYCLES(4);
            break;
        case IAG:
            RAM(dst) = IA;
            CYCLES(1);
            break;
        case IAS:
            IA = ram;
            CYCLES(1);
            break;
        case RFI:
            emulator->interrupt_queueing = 0;
            REG(0) = RAM(SP++);
            PC = RAM(SP++);
            CYCLES(3);
            break;
        case IAQ:
            emulator->interrupt_queueing = ram;
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

void do_interrupt(Emulator *emulator) {
    if (emulator->interrupt_index) {
        unsigned short message = emulator->interrupt_buffer[0];
        for (unsigned int i = 1; i < 256; i++) {
            emulator->interrupt_buffer[i - 1] =
                emulator->interrupt_buffer[i];
        }
        emulator->interrupt_buffer[255] = 0;
        emulator->interrupt_index--;
        if (IA) {
            emulator->interrupt_queueing = 1;
            RAM(--SP) = PC;
            RAM(--SP) = REG(0);
            PC = IA;
            REG(0) = message;
        }
    }
}

void one_step(Emulator *emulator) {
    do {
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
    } while (SKIP);
    on_clock_step(emulator);
    if (!emulator->interrupt_queueing) {
        do_interrupt(emulator);
    }
}

void n_steps(Emulator *emulator, unsigned int steps) {
    for (unsigned int i = 0; i < steps; i++) {
        one_step(emulator);
        if (HALT) {
            break;
        }
    }
}

void n_cycles(Emulator *emulator, unsigned int cycles) {
    unsigned long long int cycle = CYCLE + cycles;
    while (CYCLE < cycle) {
        one_step(emulator);
        if (HALT) {
            break;
        }
    }
}
