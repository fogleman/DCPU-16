#ifndef EMULATOR_H
#define EMULATOR_H

// Emulator State
typedef struct {
    // DCPU-16
    unsigned short ram[EXT_SIZE];
    unsigned short skip;
    unsigned short halt;
    unsigned long long int cycle;
    unsigned short interrupt_buffer[256];
    unsigned short interrupt_index;
    unsigned short interrupt_queueing;
    // LEM
    unsigned short lem_screen;
    unsigned short lem_font;
    unsigned short lem_palette;
    unsigned short lem_border;
    // KEYBOARD
    unsigned char keyboard_buffer[16];
    unsigned char keyboard_pressed[256];
    unsigned short keyboard_index;
    unsigned short keyboard_message;
    // CLOCK
    unsigned long long int clock_cycle;
    unsigned short clock_rate;
    unsigned short clock_ticks;
    unsigned short clock_message;
} Emulator;

// Emulator Functions
void reset(Emulator *emulator);

void load(Emulator *emulator, unsigned short *program, unsigned int length);

void interrupt(Emulator *emulator, unsigned short message);

int operand(Emulator *emulator, unsigned char x, unsigned char dereference);

int divmod(int x, int *quo);

void basic_instruction(Emulator *emulator, unsigned char opcode, 
    unsigned char op_dst, unsigned char op_src);

void on_hwq(Emulator *emulator, unsigned short index);

void on_hwi(Emulator *emulator, unsigned short index);

void special_instruction(Emulator *emulator, unsigned char opcode, 
    unsigned char op_dst);

void do_interrupt(Emulator *emulator);

void step(Emulator *emulator);

void n_steps(Emulator *emulator, unsigned int steps);

void n_cycles(Emulator *emulator, unsigned int cycles);

#endif
