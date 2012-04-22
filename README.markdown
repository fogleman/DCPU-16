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
