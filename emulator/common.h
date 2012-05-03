#ifndef COMMON_H
#define COMMON_H

// Constants
#define SIZE 0x10000
#define MAX_VALUE 0xffff
#define EXT_SIZE 0x10010
#define REG_ADDR 0x10000
#define SP_ADDR 0x10008
#define PC_ADDR 0x10009
#define EX_ADDR 0x1000a
#define IA_ADDR 0x1000b
#define LT_ADDR 0x1000c

// Helper Macros
#define NEXT_TICK (emulator->cycle + 100000 * emulator->clock_rate / 60)
#define CONDITIONAL(opcode) ((opcode) >= 0x10 && (opcode) <= 0x17)
#define CYCLES(count) (emulator->cycle += (count))
#define RAM(address) (emulator->ram[(address)])
#define REG(index) (emulator->ram[REG_ADDR + (index)])
#define SP (emulator->ram[SP_ADDR])
#define PC (emulator->ram[PC_ADDR])
#define EX (emulator->ram[EX_ADDR])
#define IA (emulator->ram[IA_ADDR])
#define LT (emulator->ram[LT_ADDR])
#define SKIP (emulator->skip)
#define HALT (emulator->halt)
#define CYCLE (emulator->cycle)

// Basic Opcodes
#define SET 0x01
#define ADD 0x02
#define SUB 0x03
#define MUL 0x04
#define MLI 0x05
#define DIV 0x06
#define DVI 0x07
#define MOD 0x08
#define MDI 0x09
#define AND 0x0a
#define BOR 0x0b
#define XOR 0x0c
#define SHR 0x0d
#define ASR 0x0e
#define SHL 0x0f
#define IFB 0x10
#define IFC 0x11
#define IFE 0x12
#define IFN 0x13
#define IFG 0x14
#define IFA 0x15
#define IFL 0x16
#define IFU 0x17
#define ADX 0x1a
#define SUX 0x1b
#define STI 0x1e
#define STD 0x1f

// Non Basic Opcodes
#define JSR 0x01
#define BRK 0x02
#define INT 0x08
#define IAG 0x09
#define IAS 0x0a
#define RFI 0x0b
#define IAQ 0x0c
#define HWN 0x10
#define HWQ 0x11
#define HWI 0x12

// Hardware
#define N_DEVICES 3
#define LEM 0
#define KEYBOARD 1
#define CLOCK 2

#endif
