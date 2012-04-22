import assembler
import cEmulator
import emulator
import time

def benchmark(name, module, program):
    print 'Benchmarking "%s" emulator using "%s"...' % (name, program)
    emu = module.Emulator()
    emu.load(assembler.assemble_file(program))
    duration = 10
    cycles = 0
    batch = 100000
    start = time.time()
    while True:
        emu.n_cycles(batch)
        cycles += batch
        elapsed = time.time() - start
        if elapsed > duration:
            break
    cycles_per_second = int(cycles / elapsed)
    print 'Result: %d cycles per second' % cycles_per_second
    print

if __name__ == '__main__':
    program = 'programs/life.dasm'
    benchmark('Python', emulator, program)
    benchmark('C', cEmulator, program)
