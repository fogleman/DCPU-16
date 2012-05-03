#include "common.h"
#include "emulator.h"
#include "keyboard.h"

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
    if (emulator->keyboard_index < 16) {
        emulator->keyboard_buffer[emulator->keyboard_index++] = key;
        if (emulator->keyboard_message) {
            interrupt(emulator, emulator->keyboard_message);
        }
    }
}

void on_keyboard(Emulator *emulator) {
    switch (REG(0)) {
        case 0: // CLEAR_BUFFER
            for (unsigned int i = 0; i < 16; i++) {
                emulator->keyboard_buffer[i] = 0;
            }
            emulator->keyboard_index = 0;
            break;
        case 1: // GET_CHARACTER
            if (emulator->keyboard_index) {
                REG(2) = emulator->keyboard_buffer[0];
                for (unsigned int i = 1; i < 16; i++) {
                    emulator->keyboard_buffer[i - 1] =
                        emulator->keyboard_buffer[i];
                }
                emulator->keyboard_buffer[15] = 0;
                emulator->keyboard_index--;
            }
            else {
                REG(2) = 0;
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
