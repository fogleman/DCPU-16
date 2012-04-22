## Python scripts for DCPU-16 emulation

- Assembler
- Emulator (Two implementations: C and Python)
- 32x12 Character, 128x96 Pixel Display

### Video

- http://www.youtube.com/watch?v=qIyYhIZ0VqI

### Screenshot

![](https://raw.github.com/fogleman/DCPU-16/master/screenshots/screenshot.png)

### Dependencies
- **Python 2.5+**: http://www.python.org/
- **PLY**: http://www.dabeaz.com/ply/
- **wxPython**: http://www.wxpython.org/

### Usage

Run a program with the visualizer.

    python display.py programs/minesweeper.dasm

Assemble and output in pretty format.

    python assemble.py programs/example.dasm

Run benchmarks on the C emulator and Python emulator to test performance.

    python benchmark.py

### Benchmark Results

MacBook Air (1.7 GHz Intel Core i5)

    Benchmarking "Python" emulator using "programs/life.dasm"...
    Result: 241310 cycles per second
    
    Benchmarking "C" emulator using "programs/life.dasm"...
    Result: 88728989 cycles per second

The C implementation is roughly 360 times faster than the Python implementation and could emulate over 800 DCPU-16 processors at their 100 kHz clock rate.
