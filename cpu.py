"""CPU functionality."""

import sys

# TODO
# Add CMP instruction and equal flag
# add JMP instruction
# add JEQ
# add JNE


class CPU:
    """Main CPU class."""

    def __init__(self):
        """ Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8              # Register / 8 bit
        self.pc = 0                     # Program Counter
        self.sp = 7                     # Stack Pointer
        self.address = 0                # Iterates in load()
        self.isPaused = False           # True when HLT()
        # ------------------------------MVP
        self.E = 0                      # Equal flag
        self.L = 0                      # Less-than flag
        self.G = 0                      # Greater-than flag
        # ------------------------------MVP
        self.branchtable = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            # -----------------------MVP
            0b10100111: self.CMP,   #
            0b01010100: self.JMP,   #
            0b01010101: self.JEQ,   #
            0b01010110: self.JNE    #
            # -----------------------MVP
        }

    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]
        with open(filename) as file:
            for line in file:
                instruction = line.split("#")
                instruction[0] = instruction[0].strip()
                if instruction[0] == '':
                    continue
                value = int(instruction[0], 2)
                self.ram[self.address] = value
                self.address += 1

    def alu(self, opcode, reg_a, reg_b):
        """Arithmetic Logic Unit operations."""
        if opcode == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif opcode == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif opcode == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.E = 1
            if self.reg[reg_a] < self.reg[reg_b]:
                self.L = 1
            if self.reg[reg_a] > self.reg[reg_b]:
                self.G = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """ Handy function to print out the CPU state. You might want to call this from run() if you need help debugging. """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def run(self):
        """Run the CPU."""
        while not self.isPaused:
            ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)
            if ir in self.branchtable:
                self.branchtable[ir](operand_a, operand_b)
            else:
                raise Exception(
                    f'Unknown Instruction {bin(ir)} at {hex(self.pc)}')
            instruction_size = (ir >> 6) + 1
            instruction_sets_pc = ((ir >> 4) & 0b1) == 1
            if not instruction_sets_pc:
                self.pc += instruction_size

    def HLT(self, operand_a, operand_b):
        self.isPaused = True

    def LDI(self, operand_a, operand_b):
        ''' Set the value of a register to an integer. '''
        self.reg[operand_a] = operand_b

    def PRN(self, operand_a, operand_b):
        ''' Print numeric value stored in the given register. '''
        print(self.reg[operand_a])

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)

    def PUSH(self, operand_a, operand_b):
        ''' Push the value in the given register on the stack. '''
        self.stack_push(self.reg[operand_a])

    def POP(self, operand_a, operand_b):
        ''' Pop the value at the top of the stack into the given register. '''
        self.reg[operand_a] = self.stack_pop()

    def CALL(self, operand_a, operand_b):
        ''' Calls a subroutine (function) at the address stored in the register. '''
        self.stack_push(self.pc + 2)
        self.pc = self.reg[operand_a]

    def RET(self, operand_a, operand_b):
        ''' Return from subroutine. '''
        self.pc = self.stack_pop()

# ----------------------------------------------------------MVP
    def CMP(self, operand_a, operand_b):
        ''' Compare the values in two registers. '''
        self.alu("CMP", operand_a, operand_b)

    def JMP(self, operand_a, operand_b):
        ''' Jump to the address stored in the given register. '''
        self.pc = self.reg[operand_a]

    def JEQ(self, operand_a, operand_b):
        if self.E == 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def JNE(self, operand_a, operand_b):
        if self.E == 0:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
# ----------------------------------------------------------MVP

    def stack_push(self, value):
        ''' Push the value in the given register on the stack. '''
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], value)

    def stack_pop(self):
        ''' Pop the value at the top of the stack into the given reg. '''
        value = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        return value

    def ram_read(self, address):
        ''' Access the RAM inside the CPU object. '''
        return self.ram[address]

    def ram_write(self, address, value):
        ''' Sets a given value to the ram with a given address. '''
        self.ram[address] = value
