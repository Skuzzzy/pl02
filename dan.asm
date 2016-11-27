bits 32
extern printf
global main
	SECTION .data
dfmt: db "%d", 10, 0
	SECTION .text
; ('main', ('FUNC main', 0))
main:
push ebp
mov ebp, esp
sub esp, 12

; Local Variables
; ('A', ('NEW A', 1)) is [ebp-4]
; ('B', ('NEW B', 2)) is [ebp-8]
; ('RET', ('NEW RET', 5)) is [ebp-12]

; ('SET A 10', 3)
mov edx, 10
mov [ebp-4], edx

; ('SET B 13', 4)
mov edx, 13
mov [ebp-8], edx

; ('FUNCALL countdown A RET', 6)
push dword [ebp-4]
call countdown
mov [ebp-12], eax
add esp, 4*1

; ('PRINT RET', 7)
push dword [ebp-12]
push dword dfmt
call printf
add esp, 4*2

; ('RETURN 0', 8)
mov eax, 0
mov eax, 0

mov esp, ebp
pop ebp
ret


; ('countdown', ('FUNC countdown', 0))
countdown:
push ebp
mov ebp, esp
sub esp, 4

; Parameters
; ('N', ('PARAM N', 1)) is [ebp+8]

; Local Variables
; ('a', ('NEW a', 4)) is [ebp-4]

; ('!loop1', 2)
loop1:

; ('JEQ N 0 endloop1', 3)
mov edx, [ebp+8]
mov ecx, 0
cmp edx, ecx
je endloop1

; ('FUNCALL nested N a', 5)
push dword [ebp+8]
call nested
mov [ebp-4], eax
add esp, 4*1

; ('SUB N 1', 6)
mov edx, 1
sub dword [ebp+8], edx

; ('JUMP loop1', 7)
jmp loop1

; ('!endloop1', 8)
endloop1:

; ('RETURN 0', 9)
mov eax, 0
mov eax, 0

mov esp, ebp
pop ebp
ret


; ('nested', ('FUNC nested', 0))
nested:
push ebp
mov ebp, esp
sub esp, 16

; Parameters
; ('Z', ('PARAM Z', 1)) is [ebp+8]

; Local Variables
; ('A', ('NEW A', 2)) is [ebp-4]
; ('B', ('NEW B', 3)) is [ebp-8]
; ('C', ('NEW C', 4)) is [ebp-12]
; ('D', ('NEW D', 5)) is [ebp-16]

; ('PRINT Z', 6)
push dword [ebp+8]
push dword dfmt
call printf
add esp, 4*2

; ('RETURN Z', 7)
mov eax, [ebp+8]
mov eax, [ebp+8]

mov esp, ebp
pop ebp
ret


