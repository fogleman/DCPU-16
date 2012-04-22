## Python scripts for DCPU-16 emulation

### Usage: Visualizer

    python display.py programs/minesweeper.dasm

Run the specified program with the visualizer. See video here: http://www.youtube.com/watch?v=qIyYhIZ0VqI

![](https://raw.github.com/fogleman/DCPU-16/master/screenshots/screenshot.png)

### Usage: Benchmarks

    python benchmark.py

Run benchmarks on the C emulator and Python emulator to test performance.

MacBook Air (1.7 GHz Intel Core i5)

    Benchmarking "Python" emulator using "programs/life.dasm"...
    Result: 241310 cycles per second
    
    Benchmarking "C" emulator using "programs/life.dasm"...
    Result: 88728989 cycles per second

The C implementation is roughly 360 times faster than the Python implementation and could emulate over 800 DCPU-16 processors at their 100 kHz clock rate.

### Usage: Pretty Print

    python assembler.py programs/example.dasm

Assemble and output in pretty format. Just like Notch's example, except comments are not retained.

        SET A, 0x0030               ; 7c01 0030
        SET [0x1000], 0x0020        ; 7de1 1000 0020
        SUB A, [0x1000]             ; 7803 1000
        IFN A, 0x0010               ; c00d
            SET PC, crash           ; 7dc1 001a
        SET I, 0x000a               ; a861
        SET A, 0x2000               ; 7c01 2000
    :loop
        SET [I + 0x2000], [A]       ; 2161 2000
        SUB I, 0x0001               ; 8463
        IFN I, 0x0000               ; 806d
            SET PC, loop            ; 7dc1 000d
        SET X, 0x0004               ; 9031
        JSR testsub                 ; 7c10 0018
        SET PC, crash               ; 7dc1 001a
    :testsub
        SHL X, 0x0004               ; 9037
        SET PC, POP                 ; 61c1
    :crash
        SET PC, crash               ; 7dc1 001a

### Dependencies
- **Python 2.5+**: http://www.python.org/
- **PLY**: http://www.dabeaz.com/ply/
- **wxPython**: http://www.wxpython.org/
