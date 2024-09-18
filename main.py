import random

# RAM of the emulator
memory = [0] * 4096

# 16 registers
registers = [0] * 16

# index register
I = 0

# screen
screen = [0] * ( 64 * 32 )

# stack
stack = []

# the program counter, starting in the memory address 0x200
pc = 0x200

# loading the ROM contents into the memory
with open("romfile.bin", "rb") as file:
    rom = file.read() # read all the binary data

    for i in range(len(rom)):
        memory [pc + i] = rom[i] # load each byte into the memory


# font
font = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
	0x20, 0x60, 0x20, 0x20, 0x70, # 1
	0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
	0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
	0x90, 0x90, 0xF0, 0x10, 0x10, # 4
	0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
	0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
	0xF0, 0x10, 0x20, 0x40, 0x40, # 7
	0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
	0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
	0xF0, 0x90, 0xF0, 0x90, 0x90, # A
	0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
	0xF0, 0x80, 0x80, 0x80, 0xF0, # C
	0xE0, 0x90, 0x90, 0x90, 0xE0, # D
	0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
	0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]

# load font into memory
for i in range(len(font)):
    memory[0x50 + i] = font[i]


# fetch execute loop
while True:

    # fetch instructions
    instruction = (memory[pc] << 8) | memory[pc + 1]
    pc += 2


    # decode instructions

    # jump
    if instruction & 0xf000 == 0x1000:
        address = instruction & 0x0fff
        pc = address

    # call subroutine
    elif instruction & 0xf000 == 0x2000:
        address = instruction & 0x0fff
        stack.append(pc + 2)
        pc = address

    # clear screen
    elif instruction & 0xffff == 0x00e0:
        screen = [0] * (64 * 32)

    # return
    elif instruction & 0xf0ff == 0x00ee:
        pc = stack.pop()

    # set value to register VX
    elif instruction & 0xf000 == 0x6000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff
        registers[x] = val

    # add value to register VX
    elif instruction & 0xf000 == 0x7000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff
        registers[x] = (registers[x] + val) & 0xff

    # set index register I
    elif instruction & 0xf000 == 0xA000:
        val = instruction & 0x0fff
        I = val

    # display / draw
    elif instruction & 0xf000 == 0xD000:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4
        n = instruction & 0x000F
        registers[0xf] = 0

        for row in range(n):
            sprite_row = memory[I + row]
            for bit in range(8):
                pixel = (sprite_row >> (7 - bit)) & 0x01
                screen_x = (x + bit) % 64
                screen_y = (y + row) % 32
                screen_idx = screen_y * 64 + screen_x
                if pixel:
                    if screen[screen_idx] == 1:
                        registers[0xf] = 1  # Pixel turned off
                    screen[screen_y][screen_x] ^= 1

    # skip if equal
    elif instruction & 0xf000 == 0x3000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff

        if registers[x] == val:
            pc+=4

    # skip if not equal
    elif instruction & 0xf000 == 0x4000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff

        if registers[x] != val:
            pc += 4

    # skip if value in 2 registers equal
    elif instruction & 0xf00f == 0x5000:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        if registers[x] == registers[y]:
            pc += 4

    # skip if value in 2 registers are not equal
    elif instruction & 0xf00f == 0x9000:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        if registers[x] != registers[y]:
            pc += 4

    # set value of one register to another
    elif instruction & 0xf00f == 0x8000:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[x] = registers[y]

    # binary OR
    elif instruction & 0xf00f == 0x8001:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[x] = registers[x] | registers[y]

    # binary AND
    elif instruction & 0xf00f == 0x8002:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[x] = registers[x] & registers[y]

    # logical XOR
    elif instruction & 0xf00f == 0x8003:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[x] = registers[x] ^ registers[y]

    # add value to register VX with overflow
    elif instruction & 0xf00f == 0x8004:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4
        val = instruction & 0x00ff
        registers[x] = (registers[x] + registers[y])

        if registers[x] > 0xff:
            registers[0xf] = 1
            registers[x] &= 0xff
        else:
            registers[0xf] = 0

    # subtract value from two registers
    elif instruction & 0xf00f == 0x8005:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[0xf] = 1

        # set the carry bit to 0 if there is a underflow
        if registers[y] > registers[x]:
            registers[0xf] = 0

        registers[x] = (registers[x] - registers[y]) & 0xff

    # shift to the right
    elif instruction & 0xf00f == 0x8006:
        x = (instruction & 0x0f00) >> 8

        registers[0xf] = registers[x] & 0x1 # store the value in the flag register rather than variable
        registers[x] = registers[x] >> 1

    # shift to the left
    elif instruction & 0xf00f == 0x800E:
        x = (instruction & 0x0f00) >> 8

        registers[0xf] = (registers[x] & 0x80) >> 7  # Store the most significant bit in VF (carry flag)
        registers[x] = (registers[x] << 1) & 0xFF  # Shift left by 1, ensuring it stays 8-bit

    # jump with offset
    elif instruction & 0xf000 == 0xb000:
        address = instruction & 0x0fff
        pc = address + registers[0]

    # random number AND
    elif instruction & 0xf000 == 0xc000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff
        random_num = (random.randint(0, 255)) & val 

        registers[x] = random_num

