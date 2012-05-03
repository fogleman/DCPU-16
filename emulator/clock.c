#include "common.h"
#include "emulator.h"
#include "clock.h"

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

void on_clock_step(Emulator *emulator) {
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
