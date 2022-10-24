import numpy as np
from bitvec import Binary
from bitvec import arithm
from bitvec.alias import u16, i16, u8, i6, u3, u4

class MyEmulator:
    PC = 7
    FLAGS = 6

    def __init__(self):
        # registers are 16 bit (initialized with 0)
        self.registers = [u16() for _ in range(8)]
        
        # memory for rom 
        self.rom = np.zeros((1024), dtype='uint16')
        
        # memory for ram 
        self.rom = np.zeros((1024), dtype='uint16')

        # flag that indicates if emulator should run
        self.should_run = True
    
    def load_rom(self, instructions):
        for i, instruction in enumerate(instructions):
            self.rom[i] = int(instruction)
    def set_flag(self, of: bool):
        self.registers[self.FLAGS] = u16(1 if of else 0)
    def execute(self):
        instr = u16(self.rom[self.registers[self.PC].int()])
        
        # 0000 000 000 000000
        # oooo r1  r2  
        
        # slice instruction into arguments
        opcode = instr[0:4]        # first 4 bit are opcode
        reg1   = instr[4:7].int()  # next 3 bits are register 1
        reg2   = instr[7:10].int() # next 3 bits are register 2

        #print(instr)
        #print(self.registers[self.PC].int(), opcode.hex(), [r.hex() for r in self.registers], sep='\t')
        
        if opcode == 1: 
            # take first byte as it is imm value
            imm = instr.low_byte()
            self.load_imm_low(reg1, imm)
        elif opcode == 2:
            self.add_regs(reg1, reg2)
        elif opcode == 3:
            self.sub_regs(reg1, reg2)
        elif opcode == 4:
            # cast imm to signed and use it as offset
            offset = arithm.cast(instr[10:16], 'signed').int()
            self.jge(reg1, reg2, offset)
        elif opcode == 5:
            offset = arithm.cast(instr[10:16], 'signed').int()
            self.jne(reg1, reg2, offset)
        elif opcode == 6:
            self.print(reg1)
        elif opcode == 7:
            self.stop()
        elif opcode == 8:
            self.mov(reg1, reg2)
        elif opcode == 0:
            self.nop()
        else:
            raise NotImplementedError # todo more commands

        self.registers[self.PC] += 1

        return self.should_run
    
    #########################
    # instructions 
    #########################
    def load_imm_low(self, reg: int, imm: Binary):
        # [:8] sets only the first 8 bits of the register to imm
        self.registers[reg][:8] = imm
    
    def mov(self, reg1, reg2):
        # [:] ensuers that regiser size is not changed
        self.registers[reg1][:] = self.registers[reg2]
    
    def add_regs(self, reg1: int, reg2: int):
        # overflowing add will return the result and a flag if overflow occured
        self.registers[reg1][:], of = arithm.overflowing_add(self.registers[reg1], self.registers[reg2])
        self.set_flag(of)
    
    def sub_regs(self, reg1: int, reg2: int):
        self.registers[reg1][:], of = arithm.overflowing_sub(self.registers[reg1], self.registers[reg2])
        self.set_flag(of)
    
    def jge(self, reg1: int, reg2: int, offset: int):
        # compare registers as unsigned values bsc we declared them as unsigned
        if self.registers[reg1] >= self.registers[reg2]:
            self.registers[self.PC][:] = self.registers[self.PC] + arithm.cast(i16(offset), 'unsigned')
    
    def jne(self, reg1: int, reg2: int, offset: int):
        if self.registers[reg1] != self.registers[reg2]:
            self.registers[self.PC][:] = self.registers[self.PC] + arithm.cast(i16(offset), 'unsigned')
    
    def print(self, reg: int):
        print(self.registers[reg].int())
    def stop(self):
        self.should_run = False
    def nop(self):
        pass

if __name__ == '__main__':
    machine = MyEmulator()
    
    # Aliases for convenience
    r   = u3
    imm = u8
    j   = i6
    # {"nop":0000, "load":0001, ... }
    op  = { opcode: u4(n) for n, opcode in enumerate(['nop', 'load', 'add', 'sub', 'jge', 'jne', 'print', 'stop', 'mov']) }

    # instruction leyout
    # 0000 000 000 000000
    # op   r1  r2  imm
    # 0000 000 0000000
    # op   r1  imm 

    # fibonnaci sequence
    program = [
        arithm.concat(imm(0),         r(1), op['load'] ), # load 1 into r1
        arithm.concat(imm(1),         r(2), op['load'] ), # load 1 into r2
        arithm.concat(imm(15),        r(3), op['load'] ), # load 15 into r3
        arithm.concat(imm(1),         r(4), op['load'] ), # load 1 into r4
        arithm.concat(          r(1), r(2), op['add']  ), # add r1 to r2
        arithm.concat(                r(2), op['print']), # print r2
        arithm.concat(          r(4), r(3), op['sub']  ), # sub 1 from r3
        arithm.concat(          r(1), r(5), op['mov']  ), # mov r1 to r5
        arithm.concat(          r(2), r(1), op['mov']  ), # mov r2 to r1
        arithm.concat(          r(5), r(2), op['mov']  ), # mov r5 to r2
        arithm.concat(j(-7),    r(4), r(3), op['jne']  ), # jne r3, r4, -6
        arithm.concat(                      op['stop'] ), # stop
    ]

    machine.load_rom(program)
    
    while machine.execute():
        pass

    print('done')
