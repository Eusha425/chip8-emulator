# CHIP-8 Emulator

A Python-based CHIP-8 emulator implementation. This project serves as my first venture into emulation development, providing a functional emulator that can run classic CHIP-8 games and programs.

## Overview

CHIP-8 is an interpreted programming language developed in the 1970s. It was initially used on the COSMAC VIP and Telmac 1800 8-bit microcomputers to make game programming easier. This emulator implements the original CHIP-8 interpreter, allowing you to run classic games and programs written for the platform.

## Features

- Complete implementation of all CHIP-8 instructions
- Sound support using PyGame
- Keyboard input mapping matching the original COSMAC VIP layout
- Display rendering at 60 FPS
- Support for loading and running ROM files
- Configurable instruction execution speed

## Prerequisites

- Python 3.7+
- PyGame
- NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Eusha425/chip8-emulator.git
cd chip8-emulator
```

2. Install required dependencies:
```bash
pip install pygame numpy
```

## Usage

1. Place your CHIP-8 ROM file in the `roms` directory
2. Run the emulator:
```bash
python main.py
```

### Keyboard Layout

The original CHIP-8 used a 16-key hexadecimal keypad. This emulator maps those keys to your keyboard as follows:

```
CHIP-8 Key   Keyboard
---------   ---------
1 2 3 C     1 2 3 4
4 5 6 D     Q W E R
7 8 9 E     A S D F
A 0 B F     Z X C V
```

## Project Structure

```
chip8-emulator/
├── main.py    # Contains all emulator logic including CPU, memory, display, and input handling
└── roms/      # Directory for ROM files
```

All emulator functionality is currently contained in `main.py`, including:
- Memory management and ROM loading
- CPU instruction processing
- Display rendering
- Keyboard input handling
- Sound generation
- Main emulation loop

## Implementation Details

The emulator implements the standard CHIP-8 specifications:
- 4KB (4096 bytes) of memory
- 16 8-bit registers (V0-VF)
- 16-bit index register (I)
- 16-bit program counter (PC)
- 64x32 pixel monochrome display
- 16-key hexadecimal keypad
- Two timers (delay and sound) counting at 60 Hz

## Testing

This emulator has been tested using the [CHIP-8 Test Suite](https://github.com/Timendus/chip8-test-suite) to ensure correct implementation of all instructions and features.

## Resources and Acknowledgments

This project was made possible thanks to the following excellent resources:

- [Guide: Writing a CHIP-8 Emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/) by Tobias V. Langhoff - This guide provided the foundational knowledge and step-by-step guidance for implementing the CHIP-8 system.
- [Cowgod's CHIP-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) - An invaluable technical reference that helped ensure accurate implementation of all CHIP-8 instructions.
- [CHIP-8 Test Suite](https://github.com/Timendus/chip8-test-suite) by Timendus - Used to verify the correctness of the emulator's implementation.

## Learning Experience

This project represents my first step into emulator development. Throughout the development process, I learned about:
- Computer architecture and memory management
- Instruction decoding and execution cycles
- Display rendering and timing
- Input handling and sound generation
- The importance of code organization (though my implementation is in a single file, I learned how it could benefit from modularization)

## Future Improvements

- Split the code into modules for better organization
- Add configuration file for customizable settings
- Implement save states
- Add debugging features
- Support for Super CHIP-8 instructions
- GUI for ROM selection and emulator settings

## License

This project is open source and available under the MIT License.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Eusha425/chip8-emulator/issues) if you want to contribute.

---

*Note: This is my first emulator project, created as a learning experience. While I've aimed to make it as accurate as possible, there might be areas for improvement.*
