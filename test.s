.extern print_int
.extern print_bool
.extern read_int
.global main
.type main, @function
.section .text
main:
push rbp
mov rbp, rsp
sub rsp, 40

# Label(Start)
.LStart:

# LoadBoolConst(True, v0)
mov [rbp-8], 1

# Copy(v0, v1)
mov %rax, [rbp-8]
mov [rbp-16], %rax

# CondJump(v1, Label(L0), Label(L1))

# Label(L0)
.LL0:

# LoadIntConst(1, v2)
mov [rbp-24], 1

# Jump(Label(L2))
jmp .LL2

# Label(L1)
.LL1:

# LoadIntConst(2, v3)
mov [rbp-32], 2

# Label(L2)
.LL2:

# Return()
mov rax, 0
mov rsp, rbp
pop rbp
ret
