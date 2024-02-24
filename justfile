build-asm:
  clang test.s -mllvm -g -Wl,-pie -o test.out

run-asm: build-asm
  ./test.out
