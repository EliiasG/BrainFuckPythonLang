import sys
def comp(prgm):
    indent = 0
    i=0
    compiled = ""
    compiled += "ptr = 0\n"
    compiled += "mem = [0]*30000\n"
    c1=0
    c2=0
    c3=0
    c4=0
    li = 0
    for c in prgm:
        i += 1
        line = ""

        if c == "<":
            c1 += 1
        if c == ">":
            c2 += 1
        if c == "+":
            c3 += 1
        if c == "-":
            c4 += 1

        if c != "<" and c1 > 0:
            line = f"ptr -= {c1}"
            c1=0
        if c != ">" and c2 > 0:
            line = f"ptr += {c2}"
            c2=0
        if c != "+" and c3 > 0:
            line = f"mem[ptr] += {c3}"
            c3=0
        if c != "-" and c4 > 0:
            line = f"mem[ptr] -= {c4}"
            c4=0

        if line != "":
            compiled += "    "*li + line + "\n"
            line = ""
        
        if c == ".":
            line = "print(chr(mem[ptr]), end=\"\")"
        if c == ",":
            line = "mem[ptr] = ord(input())"
        if c == "[":
            line = "while mem[ptr] > 0:"
            indent += 1
        if c == "]":
            indent -= 1
            #line = "#close"

        if line != "":
            compiled += "    "*li + line + "\n"
        li = indent
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