#ifndef KEYBOARD_H
#define KEYBOARD_H

#include "emulator.h"

void on_key_down(Emulator *emulator, unsigned char key);

void on_key_up(Emulator *emulator, unsigned char key);

void on_char(Emulator *emulator, unsigned char key);

void on_keyboard(Emulator *emulator);

#endif
