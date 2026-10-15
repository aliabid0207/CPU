Source:
; ---------- CPU TEST 2: loads, stores, bytes, stack (needs RAM at 0x00100000) ----------
        LI   SP, 0x00200000
        LI   R1, 0x00100000
        LUI  R2, 0x01234567
        ORI  R2, R2, 0x89ABCDEF  ; R2 = 0x0123456789ABCDEF
        SD   R2, [R1+0]
        LD   R3, [R1+0]
        CMP  R3, R2
        BNE  f1
        LBU  R3, [R1+0]          ; 0xEF
        CMPI R3, 0xEF
        BNE  f2
        LB   R3, [R1+0]          ; -17
        CMPI R3, -17
        BNE  f3
        LBU  R3, [R1+7]          ; 0x01
        CMPI R3, 1
        BNE  f4
        LHU  R3, [R1+2]          ; 0x89AB
        CMPI R3, 0x89AB
        BNE  f5
        LWU  R3, [R1+4]          ; 0x01234567
        CMPI R3, 0x01234567
        BNE  f6
        LI   R4, 0x41
        SB   R4, [R1+3]          ; change byte 3 only
        LD   R3, [R1+0]
        LUI  R5, 0x01234567
        ORI  R5, R5, 0x41ABCDEF
        CMP  R3, R5
        BNE  f7
        LI   R4, 0x7777
        SH   R4, [R1+6]          ; top 16 bits
        LHU  R3, [R1+6]
        CMPI R3, 0x7777
        BNE  f8
        LBU  R3, [R1+5]          ; byte 5 untouched = 0x45
        CMPI R3, 0x45
        BNE  f9
        LI   R6, 10
        CALL sum                 ; R6 = 10+9+...+1 = 55 (recursive, uses the stack)
        CMPI R6, 55
        BNE  f10
        LI   R3, 0x00200000
        CMP  SP, R3              ; stack pointer back where it started
        BNE  f11
pass:   HLT
sum:    CMPI R6, 0
        BEQ  sret
        ADDI SP, SP, -16
        SD   LR, [SP+0]
        SD   R6, [SP+8]
        ADDI R6, R6, -1
        CALL sum
        LD   R7, [SP+8]
        ADD  R6, R6, R7
        LD   LR, [SP+0]
        ADDI SP, SP, 16
sret:   RET
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