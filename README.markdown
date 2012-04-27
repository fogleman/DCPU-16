## DCPU-16 Emulator v1.7

### Download (Windows Installer)

http://static.michaelfogleman.com/static/dcpu16-setup.exe

### Implemented Specifications

- DCPU-16 1.7: http://pastebin.com/raw.php?i=Q4JvQvnM
- LEM1802: http://dcpu.com/highnerd/rc_1/lem1802.txt
- Generic Keyboard: http://dcpu.com/highnerd/rc_1/keyboard.txt
- Generic Clock: http://dcpu.com/highnerd/rc_1/clock.txt

### Screenshots

![](https://raw.github.com/fogleman/DCPU-16/master/screenshots/debug.png)

![](https://raw.github.com/fogleman/DCPU-16/master/screenshots/editor.png)

### Assembler Features

    ; String Literals
    DAT "Here is some text.", 0 ; null-terminated string
    
    ; Character Literals
    SET A 'a' ; A = 0x61
    SET B 'A' ; B = 0x41
    
    ; Negative Numbers
    SET A -1    ; A = 0xffff
    SET B -0xff ; B = 0xff01
    
    ; Breakpoints
    BRK
    
    ; Opcode Aliases
    SET A POP
    SET A [SP++] ; equivalent to POP
    
    SET PUSH A
    SET [--SP] A ; equivalent to PUSH
    
    SET A PICK 1
    SET A [SP + 1] ; equivalent to PICK 1
    
    SET A PEEK
    SET A [SP] ; equivalent to PEEK
    
    ; Local Labels
    :prefix
      SET A 10
    :.loop ; becomes prefix.loop
      SUB A 1
      IFE A 0
        SET PC .done
      SET PC .loop
    :.done ; becomes prefix.done
    
    ; Fixed Labels
    :screen @ 0x8000

### Upgrading from v1.1

Quickly get up and running for most programs using this code at the beginning.

    ; map screen
    SET A 0
    SET B 0x8000
    HWI 0
    ; map font (only if using a custom font)
    SET A 1
    SET B 0x8180
    HWI 0

### Benchmarks

    Usage: python benchmark.py

Run benchmarks on the emulator to test performance.

MacBook Air (1.7 GHz Intel Core i5)

    Benchmarking "C" emulator using "programs/life.dasm"...
    Result: 88728989 cycles per second

The C implementation could emulate over 800 DCPU-16 processors at their 100 kHz clock rate.

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
