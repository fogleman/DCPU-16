gcc -std=c99 -O3 -c emulator\*.c
gcc -shared -o _emulator.dll *.o
del *.o
