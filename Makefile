
all:
	python treelang.py > dan.asm
	nasm -felf32 dan.asm
	gcc -m32 -lgcc -o a.out dan.o

