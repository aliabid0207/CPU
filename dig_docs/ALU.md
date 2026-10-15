# Circuit: ALU

Source file: `ALU.dig` (Digital circuit).

## Inputs
- A: 64 bits
- B: 64 bits
- OP: 4 bits

## Outputs
- C: 1 bits
- OUT: 64 bits
- Z: 1 bits
- N: 1 bits
- V: 1 bits

## Subcircuits used
- ALU uses the [[64 TO 1 NOR]] circuit (1x)
- ALU uses the [[64-BIT ALU]] circuit (1x)

## Built-in parts
- Splitter: 5
- XOr: 3
- BarrelShifter: 3
- And: 2
- Ground: 2
- Decoder: 1
- Multiplexer: 1
- Or: 1

## Labelled parts
- SAR (BarrelShifter, 64 bits)
- SHR (BarrelShifter, 64 bits)
- SHL (BarrelShifter, 64 bits)

## Test cases
- unnamed
