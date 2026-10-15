        LI   R1, 5
        LI   R2, 3
        ADD  R3, R1, R2         ; 8
        CMPI R3, 8
        BNE  f1
        SUB  R3, R1, R2         ; 2
        CMPI R3, 2
        BNE  f2
        SUB  R3, R2, R1         ; -2
        CMPI R3, -2
        BNE  f3
        LI   R4, 0x0F0
        LI   R5, 0x0FF
        AND  R6, R4, R5         ; 0xF0
        CMPI R6, 0xF0
        BNE  f4
        OR   R6, R4, R2         ; 0xF3
        CMPI R6, 0xF3
        BNE  f5
        XOR  R6, R4, R5         ; 0x0F
        CMPI R6, 0x0F
        BNE  f6
        SHLI R6, R1, 4          ; 80
        CMPI R6, 80
        BNE  f7
        SHRI R6, R6, 2          ; 20
        CMPI R6, 20
        BNE  f8
        LI   R6, -16
        SARI R6, R6, 2          ; -4
        CMPI R6, -4
        BNE  f9
        LUI  R7, 1              ; 0x100000000
        SHRI R7, R7, 32         ; 1
        CMPI R7, 1
        BNE  f10
        CMP  R2, R1             ; 3 vs 5
        BGE  f11                ; signed: 3 >= 5 is false
        BLT  t1
        JMP  f12
t1:     LI   R8, -1
        CMP  R8, R1             ; -1 vs 5
        BLTU f13                ; unsigned: 0xFFFF.. < 5 is false
        BLT  t2                 ; signed: -1 < 5 is true
        JMP  f14
t2:     CMP  R1, R1
        BNE  f15
        BEQ  t3
        JMP  f16
t3:     BGEU t4                 ; equal -> C = 1
        JMP  f17
t4:     LI   R9, 0
        CALL sub
        CMPI R9, 42
        BNE  f18
        ADD  R0, R1, R2         ; write to R0 is ignored
        CMP  R0, R0
        BNE  f19
        CMPI R0, 0
        BNE  f20
pass:   HLT
sub:    LI   R9, 42
        RET
f1:     HLT
f2:     HLT
f3:     HLT
f4:     HLT
f5:     HLT
f6:     HLT
f7:     HLT
f8:     HLT
f9:     HLT
f10:    HLT
f11:    HLT
f12:    HLT
f13:    HLT
f14:    HLT
f15:    HLT
f16:    HLT
f17:    HLT
f18:    HLT
f19:    HLT
f20:    HLT