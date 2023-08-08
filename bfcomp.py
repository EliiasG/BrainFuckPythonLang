import sys

def comp(prgm):
    indent = 0
    compiled = ""
    compiled += "ptr = 0\n"
    compiled += "mem = [0]*30000\n"
    for c in prgm:
        compiled += "    " * indent
        if c == ".":
            compiled += "print(chr(mem[ptr]), end=\"\")"
        if c == ",":
            compiled += "mem[ptr] = ord(input())"
        if c == "<":
            compiled += "ptr -= 1"
        if c == ">":
            compiled += "ptr += 1"
        if c == "+":
            compiled += "mem[ptr] += 1"
        if c == "-":
            compiled += "mem[ptr] -= 1"
        if c == "[":
            compiled += "while mem[ptr] > 0:"
            indent += 1
        if c == "]":
            indent -= 1
        compiled += "\n"
    return compiled

if not len(sys.argv) in range(2, 4):
    print("supply 1 or 2 arguments")
    exit()

f = open(sys.argv[1], "r")
src = f.read()
f.close()
c = comp(src)
if len(sys.argv) == 2:
    eval(c)
else:
    rf = open(sys.argv[2], "w")
    rf.write(c)
    rf.close()