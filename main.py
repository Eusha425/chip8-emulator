import random
import pygame
import numpy as np

# function to render the screen
def draw_screen():

    for y in range(32):
        for x in range(64):
            # if 1 is found in the binary, set the screen color to white
            if screen[y * 64 + x] == 1:
                color = WHITE
            else:
                color = BLACK
            pygame.draw.rect(window, color, pygame.Rect(x * 10, y * 10, 10, 10))
    pygame.display.update()

# color values of the screen
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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

delay_timer = 0
sound_timer = 0

# keyboad mapping to the COSMAC VIP keypad
keyboard = {
    pygame.K_1 : 0x1, 
    pygame.K_2 : 0x2,
    pygame.K_3 : 0x3,
    pygame.K_4 : 0xc,
    pygame.K_q : 0x4,
    pygame.K_w : 0x5,
    pygame.K_e : 0x6,
    pygame.K_r : 0xd,
    pygame.K_a : 0x7,
    pygame.K_s : 0x8,
    pygame.K_d : 0x9,
    pygame.K_f : 0xe,
    pygame.K_z : 0xa,
    pygame.K_x : 0x0,
    pygame.K_c : 0xb,
    pygame.K_v : 0xf
}

# loading the ROM contents into the memory
with open("5-quirks.ch8", "rb") as file:
    rom = file.read() # read all the binary data

    for i in range(len(rom)):
        memory [pc + i] = rom[i] # load each byte into the memory


# font of CHIP-8
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
    memory[0x50 + i] = font[i] # load memory from the address 0x50 as per the docs

# initialisation of the pygame object to render the screen and run the emulator
pygame.init()
# Set up display
WIDTH, HEIGHT = 64 * 10, 32 * 10 # Scaled 10x

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHIP-8 Emulator")
clock = pygame.time.Clock()

# initialise the sound
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Generate a simple sine wave for the beep
duration = 0.1  # Duration of the beep in seconds
frequency = 440  # Frequency of the beep in Hz (A4 note)
sample_rate = 44100
t = np.linspace(0, duration, int(sample_rate * duration), False)
beep_wave = np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM
beep_wave = (beep_wave * 32767).astype(np.int16)

# Make it stereo by duplicating the mono channel
beep_stereo = np.column_stack((beep_wave, beep_wave))

# Create a Pygame Sound object from the numpy array
beep = pygame.sndarray.make_sound(beep_stereo)

# fetch execute loop
while True:

    # fetch instructions
    instruction = (memory[pc] << 8) | memory[pc + 1]
    pc += 2


    # decode instructions & execute

    # jump
    if instruction & 0xf000 == 0x1000:
        address = instruction & 0x0fff
        pc = address

    # call subroutine
    elif instruction & 0xf000 == 0x2000:
        address = instruction & 0x0fff
        stack.append(pc)
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
        # ensuring using values from the registers and not just simply getting it from the opcode, thanks to chatgpt for helping with this!!!
        x = registers[(instruction & 0x0F00) >> 8]
        y = registers[(instruction & 0x00F0) >> 4]

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
                    screen[screen_idx] ^= 1
        draw_screen() # call the screen render function

    # skip if equal
    elif instruction & 0xf000 == 0x3000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff

        if registers[x] == val:
            pc+=2

    # skip if not equal
    elif instruction & 0xf000 == 0x4000:
        x = (instruction & 0x0f00) >> 8
        val = instruction & 0x00ff

        if registers[x] != val:
            pc += 2

    # skip if value in 2 registers equal
    elif instruction & 0xf00f == 0x5000:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        if registers[x] == registers[y]:
            pc += 2

    # skip if value in 2 registers are not equal
    elif instruction & 0xf00f == 0x9000:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        if registers[x] != registers[y]:
            pc += 2

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

        # reset flag
        registers[0xf] = 0

    # binary AND
    elif instruction & 0xf00f == 0x8002:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[x] = registers[x] & registers[y]

        # reset flag
        registers[0xf] = 0

    # logical XOR
    elif instruction & 0xf00f == 0x8003:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        registers[x] = registers[x] ^ registers[y]

        # reset flag
        registers[0xf] = 0

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

        vx = registers[x]
        vy = registers[y]

        # Perform the subtraction and store the result in vx
        registers[x] = (vx - vy) & 0xff

        # Set the carry flag to 0 if there is an underflow
        if vx >= vy:
            registers[0xf] = 1  # No underflow
        else:
            registers[0xf] = 0  # Underflow occurred        

    # shift to the right
    elif (instruction & 0xF00F) == 0x8006:
        x = (instruction & 0x0F00) >> 8
        y = (instruction & 0x00F0) >> 4  # Add this line to get Y
        
        # Capture the least significant bit of VY before shifting
        registers[0xF] = registers[y] & 0x1
        
        # Store shifted value of VY in VX
        registers[x] = (registers[y] >> 1) & 0xFF

    # subtract value from two registers
    elif instruction & 0xf00f == 0x8007:
        x = (instruction & 0x0f00) >> 8
        y = (instruction & 0x00f0) >> 4

        # Perform the subtraction
        registers[x] = (registers[y] - registers[x]) & 0xff

        # Set the carry flag after the calculation
        # If VY > VX, set VF to 1 (no underflow), otherwise set VF to 0 (underflow)
        if registers[y] > registers[x]:
            registers[0xf] = 1
        else:
            registers[0xf] = 0

    # shift to the left
    elif instruction & 0xf00f == 0x800E:
        x = (instruction & 0x0F00) >> 8
        y = (instruction & 0x00F0) >> 4  # Add this line to get Y
        
        # Store the most significant bit in VF (carry flag)
        registers[0xF] = (registers[y] & 0x80) >> 7
        
        # Store shifted value of VY in VX
        registers[x] = (registers[y] << 1) & 0xFF

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

    # skip if key pressed
    elif instruction & 0xf0ff == 0xe09e:
        x = (instruction & 0x0f00) >> 8
        key_value = registers[x]
        keys = pygame.key.get_pressed()
        
        # Find the pygame key corresponding to the CHIP-8 key value
        corresponding_pygame_key = None
        for pygame_key, chip8_key in keyboard.items():
            if chip8_key == key_value:
                corresponding_pygame_key = pygame_key
                break
        
        if corresponding_pygame_key and keys[corresponding_pygame_key]:
            pc += 2
            
    # skip if key not pressed
    elif instruction & 0xf0ff == 0xe0a1:
        x = (instruction & 0x0f00) >> 8
        key_value = registers[x]
        keys = pygame.key.get_pressed()
        
        # Find the pygame key corresponding to the CHIP-8 key value
        corresponding_pygame_key = None
        for pygame_key, chip8_key in keyboard.items():
            if chip8_key == key_value:
                corresponding_pygame_key = pygame_key
                break
        
        if not corresponding_pygame_key or not keys[corresponding_pygame_key]:
            pc += 2

    # set current value of delay timer
    elif instruction & 0xf0ff == 0xf007:
        x = (instruction & 0x0f00) >> 8 
        registers[x] = delay_timer
    
    # set delay timer
    elif instruction & 0xf0ff == 0xf015:
        x = (instruction & 0x0f00) >> 8
        delay_timer = registers[x]

    # set sound timer
    elif instruction & 0xf0ff == 0xf018:
        x = (instruction & 0x0f00) >> 8
        sound_timer = registers[x]
    
    # add value to the index register
    elif instruction & 0xf0ff == 0xf01e:
        x = (instruction & 0x0f00) >> 8
        I += registers[x]

    # block until key press
    elif instruction & 0xf0ff == 0xf00a:
        x = (instruction & 0x0f00) >> 8
        keys = pygame.key.get_pressed()
        
        key_pressed = False
        for pygame_key, chip8_key in keyboard.items():
            if keys[pygame_key]:
                registers[x] = chip8_key
                key_pressed = True
                break
        
        if not key_pressed:
            pc -= 2  # Stay on the same instruction if no key is pressed

    # set I to a hex character
    elif instruction & 0xf0ff == 0xf029:
        x = (instruction & 0x0f00) >> 8
        I = 0x50 + (registers[x] * 5)  # each sprite is 5 bytes long

    # Binary coded decimal conversion
    elif instruction & 0xf0ff == 0xf033:
        x = (instruction & 0x0f00) >> 8
        val = registers[x]
        hundreds = val // 100
        tens = (val // 10) % 10
        ones = val % 10
        memory[I] = hundreds
        memory[I+1] = tens
        memory[I+2] = ones

    # store memory
    elif instruction & 0xf0ff == 0xf055:
        x = (instruction & 0x0f00) >> 8
        for i in range(x + 1): # loop through all the xth registers, x inclusive
            val = registers[i]
            memory[I + i] = val # store value in memory
        
        I = I + x + 1 # increment the index register

    # load from memory
    elif instruction & 0xf0ff == 0xf065:
        x = (instruction & 0x0f00) >> 8
        for i in range(x + 1): # loop through all the xth registers, x inclusive
            val = memory[I + i]
            registers[i] = val

        I = I + x + 1 # increment the index register


    if delay_timer > 0:
        delay_timer -= 1
    if sound_timer > 0:
        sound_timer -= 1
        if sound_timer == 0:
            beep.play()

    clock.tick(60)  # Run at 60 frames per second
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

