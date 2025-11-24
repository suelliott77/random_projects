#!/usr/bin/env python3
"""
TinyVM - minimal bytecode emulator example

Usage:
    Save as tinyvm.py and run:
        python tinyvm.py program.bin
    Or run without args to run a demo program that prints numbers 0..9.

Instruction format: 1-byte opcode, optional operands (big-endian)
Opcodes:
    0x00 NOP
    0x01 HALT
    0x10 LOAD_REG_IMM  reg (1 byte) imm (4 bytes)
    0x11 MOV_REG_REG   dst (1) src (1)
    0x20 ADD_REG_REG   dst (1) src (1)    ; dst = dst + src
    0x21 SUB_REG_REG   dst (1) src (1)
    0x30 JMP           addr (4 bytes)
    0x31 JZ            reg (1) addr (4)    ; if reg == 0 jump
    0x40 PRINT_REG     reg (1)             ; print integer value
    0xF0 DEBUG_STATE   (no operands)        ; prints CPU state
This file is deliberately small and dependency-free.
"""

import sys
import struct
import time

MEMORY_SIZE = 64 * 1024
NUM_REGS = 8

class TinyVM:
        def __init__(self, memsize=MEMORY_SIZE):
                self.mem = bytearray(memsize)
                self.regs = [0] * NUM_REGS
                self.ip = 0
                self.running = False
                self.start_time = None
                self.opcount = 0

        def load(self, data, addr=0):
                self.mem[addr:addr+len(data)] = data
                self.ip = addr

        def fetch_u8(self):
                v = self.mem[self.ip]
                self.ip += 1
                return v

        def fetch_u32(self):
                v = struct.unpack_from(">I", self.mem, self.ip)[0]
                self.ip += 4
                return v

        def step(self):
                opcode = self.fetch_u8()
                self.opcount += 1

                if opcode == 0x00:            # NOP
                        return
                if opcode == 0x01:            # HALT
                        self.running = False
                        return
                if opcode == 0x10:            # LOAD_REG_IMM
                        r = self.fetch_u8()
                        imm = self.fetch_u32()
                        self.regs[r % NUM_REGS] = imm
                        return
                if opcode == 0x11:            # MOV_REG_REG
                        dst = self.fetch_u8()
                        src = self.fetch_u8()
                        self.regs[dst % NUM_REGS] = self.regs[src % NUM_REGS]
                        return
                if opcode == 0x20:            # ADD_REG_REG
                        dst = self.fetch_u8()
                        src = self.fetch_u8()
                        self.regs[dst % NUM_REGS] = (self.regs[dst % NUM_REGS] + self.regs[src % NUM_REGS]) & 0xFFFFFFFF
                        return
                if opcode == 0x21:            # SUB_REG_REG
                        dst = self.fetch_u8()
                        src = self.fetch_u8()
                        self.regs[dst % NUM_REGS] = (self.regs[dst % NUM_REGS] - self.regs[src % NUM_REGS]) & 0xFFFFFFFF
                        return
                if opcode == 0x30:            # JMP
                        addr = self.fetch_u32()
                        self.ip = addr % len(self.mem)
                        return
                if opcode == 0x31:            # JZ
                        r = self.fetch_u8()
                        addr = self.fetch_u32()
                        if self.regs[r % NUM_REGS] == 0:
                                self.ip = addr % len(self.mem)
                        return
                if opcode == 0x40:            # PRINT_REG
                        r = self.fetch_u8()
                        print(self.regs[r % NUM_REGS])
                        return
                if opcode == 0xF0:            # DEBUG_STATE
                        self.debug_state()
                        return

                # Unknown opcode: stop
                print(f"Unknown opcode 0x{opcode:02X} at {self.ip-1}")
                self.running = False

        def run(self, max_steps=10_000_000):
                self.running = True
                self.start_time = time.time()
                steps = 0
                try:
                        while self.running and steps < max_steps:
                                self.step()
                                steps += 1
                except Exception as e:
                        print("VM crashed:", e)
                        self.running = False
                elapsed = time.time() - self.start_time
                print(f"Stopped after {steps} steps, opcount={self.opcount}, elapsed={elapsed:.4f}s")

        def debug_state(self):
                regs = " ".join(f"r{i}={self.regs[i]}" for i in range(NUM_REGS))
                print(f"IP={self.ip} {regs}")

# Helper to build a program easily
def assemble_bytes(*parts):
        out = bytearray()
        for p in parts:
                if isinstance(p, int):
                        out.append(p)
                elif isinstance(p, (bytes, bytearray)):
                        out.extend(p)
                elif isinstance(p, tuple) and p[0] == "u32":
                        out.extend(struct.pack(">I", p[1]))
                else:
                        raise ValueError("unknown part")
        return out

def demo_program():
        # Demonstration program: counts 0..9 and prints each number
        # r0 = 0
        # loop:
        #   print r0
        #   r1 = 1
        #   r0 = r0 + r1
        #   if r0 == 10 jump end
        #   jump loop
        parts = []
        parts += [0x10, 0x00] + list(struct.pack(">I", 0))           # LOAD r0, 0
        parts += [0x10, 0x01] + list(struct.pack(">I", 10))          # LOAD r1, 10
        loop_addr = len(parts)
        parts += [0x40, 0x00]                                       # PRINT r0
        parts += [0x10, 0x02] + list(struct.pack(">I", 1))          # LOAD r2, 1
        parts += [0x20, 0x00, 0x02]                                 # ADD r0, r2
        parts += [0x31, 0x00] + list(struct.pack(">I", 0))          # JZ r0, addr=0 (placeholder)
        # We'll patch the JZ to jump to end when r0 == 10 by comparing r0==r1 via subtract & check zero:
        # Instead do: SUB r0, r1 ; JZ r0, end ; ADD r0, r1 (restore)
        parts = []
        parts += [0x10, 0x00] + list(struct.pack(">I", 0))           # LOAD r0,0
        parts += [0x10, 0x01] + list(struct.pack(">I", 10))          # LOAD r1,10
        loop_addr = len(parts)
        parts += [0x40, 0x00]                                       # PRINT r0
        parts += [0x10, 0x02] + list(struct.pack(">I", 1))          # LOAD r2,1
        parts += [0x20, 0x00, 0x02]                                 # ADD r0, r2
        parts += [0x11, 0x03, 0x00]                                 # MOV r3, r0
        parts += [0x21, 0x03, 0x01]                                 # SUB r3, r1   ; r3 = r0 - r1
        parts += [0x31, 0x03] + list(struct.pack(">I", 0))          # JZ r3, end (placeholder)
        parts += [0x30] + list(struct.pack(">I", loop_addr))        # JMP loop
        end_addr = len(parts)
        parts += [0x01]                                             # HALT
        # Patch JZ to point to end_addr
        jz_offset = 0
        # locate the JZ instruction index: after assembling we'll search for 0x31
        prog = bytearray(parts)
        idx = prog.find(b'\x31')
        if idx != -1:
                struct.pack_into(">I", prog, idx+2, end_addr)
        return prog

def load_file_or_demo(path=None):
        if path:
                with open(path, "rb") as f:
                        return f.read()
        return demo_program()

def main():
        path = sys.argv[1] if len(sys.argv) > 1 else None
        prog = load_file_or_demo(path)
        vm = TinyVM()
        vm.load(prog, 0)
        vm.run()

if __name__ == "__main__":
        main()