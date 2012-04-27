gcc -std=c99 -O3 -c -o _emulator.o emulator\emulator.c
gcc -shared -o _emulator.dll _emulator.o
del _emulator.o
