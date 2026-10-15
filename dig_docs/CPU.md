# Circuit: CPU

Source file: `CPU.dig` (Digital circuit).

## Inputs
- RESET: 1 bits
- MIN: 64 bits

## Outputs
- MWR: 1 bits
- MBE: 8 bits
- MOUT: 64 bits
- DBGPC: 32 bits
- MADDR: 32 bits

## Subcircuits used
- CPU uses the [[1-8 BIT DUPLICATOR]] circuit (1x)
- CPU uses the [[4 TO 1 OR]] circuit (1x)
- CPU uses the [[ALU]] circuit (1x)
- CPU uses the [[CONDITION UNIT]] circuit (1x)
- CPU uses the [[IMM]] circuit (1x)
- CPU uses the [[LOAD FORMATTER]] circuit (1x)
- CPU uses the [[REG FILE]] circuit (1x)
- CPU uses the [[STORE FORMATTER]] circuit (1x)

## Built-in parts
- Splitter: 12
- Multiplexer: 7
- Register: 6
- Ground: 4
- Or: 3
- Not: 2
- And: 2
- VDD: 2
- Const: 2
- ROM: 1
- Counter: 1
- Add: 1
- Clock: 1

## Labelled parts
- MICROCODE (ROM, 32 bits)
- IR (Register, 64 bits)
- PC (Register, 32 bits)
- CLK (Clock, 1 bits)

## Test cases
- TEST1
- TEST2
- TEST3

## Data files loaded
- microcode.hex
