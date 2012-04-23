## Python scripts for DCPU-16 emulation

### Windows Installer

http://www.michaelfogleman.com/static/dcpu16-setup.exe

### Visualizer

    Usage: python main.py [input.dasm]

![](https://raw.github.com/fogleman/DCPU-16/master/screenshots/debug.png)

![](https://raw.github.com/fogleman/DCPU-16/master/screenshots/no_debug.png)

### Benchmarks

    Usage: python benchmark.py

Run benchmarks on the C emulator and Python emulator to test performance.

MacBook Air (1.7 GHz Intel Core i5)

    Benchmarking "Python" emulator using "programs/life.dasm"...
    Result: 241310 cycles per second
    
    Benchmarking "C" emulator using "programs/life.dasm"...
    Result: 88728989 cycles per second

The C implementation is roughly 360 times faster than the Python implementation and could emulate over 800 DCPU-16 processors at their 100 kHz clock rate.

### Pretty Print

    Usage: python assembler.py programs/example.dasm > pretty_output.dasm

Assemble and output in pretty format. Shows machine code in comments. Comments from the input file are not retained.

        SET A, 48                   ; 7c01 0030
        SET [0x1000], 32            ; 7de1 1000 0020
        SUB A, [0x1000]             ; 7803 1000
        IFN A, 16                   ; c00d
            SET PC, crash           ; 7dc1 001a
        SET I, 10                   ; a861
        SET A, 0x2000               ; 7c01 2000
    :loop
        SET [I + 0x2000], [A]       ; 2161 2000
        SUB I, 1                    ; 8463
        IFN I, 0                    ; 806d
            SET PC, loop            ; 7dc1 000d
        SET X, 4                    ; 9031
        JSR testsub                 ; 7c10 0018
        SET PC, crash               ; 7dc1 001a
    :testsub
        SHL X, 4                    ; 9037
        SET PC, POP                 ; 61c1
    :crash
        SET PC, crash               ; 7dc1 001a

### Dependencies
- **Python 2.5+**: http://www.python.org/
- **PLY**: http://www.dabeaz.com/ply/
- **wxPython**: http://www.wxpython.org/
