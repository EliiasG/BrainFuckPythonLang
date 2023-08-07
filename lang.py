import sys

def genclosers(program):
    closers = {}
    stack = []
    for i in range(len(program)):
        c = program[i]
        if c == "[":
            stack.append(i)
        elif c == "]":
            start = stack.pop()
            closers[start] = i
            closers[i] = start - 1
    return closers
        
def brainfuck(program, nums):
    # map of loop start indices to loop end indices, and the opposite
    closers = genclosers(program)
    #pointer in cells
    pointer = 0
    cells = [0] * 30000
    #position in program
    pos = 0
    while pos < len(program):
        c = program[pos]
        # jump if start and pointer is 0, or jump if end - at start it jumps to end, skipping the end
        if (c == "[" and cells[pointer] == 0) or c == "]":
            pos = closers[pos]
        elif c == ">":
            pointer += 1
        elif c == "<":
            pointer -= 1
            if pointer < 0:
                print("pointer left")
                exit()
        elif c == "+":
            cells[pointer] += 1
            if cells[pointer] > 2**8-1:
                print("value overflow")
                exit()
        elif c == "-":
            cells[pointer] -= 1
            if cells[pointer] < 0:
                print("negative value")
                exit()
        elif c == ".":
            v = cells[pointer]
            print(str(v) + "\n" if nums else chr(v), end = "")
        elif c == ",":
            cells[pointer] = int(input()) if nums else ord(input())
        elif c == "d":
            print(str(pointer))
        elif c == "D":
            print(cells[:100])
        pos += 1

"""
setup:
a, b
c = a + b
r1 = 1 (res a >= b)
r2 = 1 (res b >= a)
"""
def assert_prog(prog):
    assert(compare_prog.count("[") == compare_prog.count("]"))
compare_prog = "".join([
    ">" * 9, # go c (9)
    "[" , #loop:
        "-" ,  #dec
        "<" * 4, # go a (5)
        "[" ,  # loop:
            "<<" ,     # go r2 (3)
            "[-]" ,   # set 0
            ">" * 10 , # go c0 (13)
        "]" ,
        "<[<<]", # reset
        ">" * 7 , # go b (7)
        "[" ,   # loop:
            "-" ,    #dec
            "<" * 4 ,   # go r2 (3)
            "[-]+" , # set 1
            "<<" ,    # go r1 (1)
            "[-]" ,  # set 0
            ">" * 12,# go c0 (13)
        "]" ,
        "<[<<]", # go back
        ">" * 5 , # go a (5)
        "[" ,  # loop:
            "-" ,    # dec
            "<" * 4 ,   # go r1 (1)
            "[-]+",  # set 1
            ">" * 12,# go c0 (13)
        "]",
        "<[<<]",
        ">" * 9, #go c (9)
    "]",
    "<[<<]", # go back
]) # compare_prog
assert_prog(compare_prog)
"""
setup:
a,b
c = 0
r1 = 1 (res a and b)
c = 2
"""

and_prog = "".join([
    ">>>>>", # go a (5)
    "[",  # loop:
        ">>>>", # go c (9)
        "-",  #dec
        ">>>>", # go c0 (13)
    "]",
    "<[<<]" # go back
    ">>>>>>>", # go b (7)
    "[", # loop:
        ">>", #go c (9)
        "-", #dec
        ">>>>", #go c0 (13)
    "]",
    "<[<<]", # go back
    ">>>>>>>>>", # go c (9)
    "[", # loop:
        "<<<<<<<<", # go r1 (1)
        "-", # dec
        ">>>>>>>>>>>>", # go c0 (13)
    "]",
    "<[<<]",
]) # and_prog
assert_prog(and_prog)

"""
setup:
a
r1 = 1
"""

not_prog = "".join([
    ">>>>>", #go a (5)
    "[", # loop:
        "<<<<", # go r1 (1)
        "-", # dec
        ">>>>>>>>>>>>", # go c0 (13)
    "]",
    "<[<<]" # reset
])
assert_prog(not_prog)


"""
example list
S0F_E_E_E_E_E_E...0
where E means element S means element to store and F means fetched element
"""

"""
setup:
starts after F
value after F is index to ready to (0-index)
ends on space after index to ready to
"""

list_ready_prog = "".join([
    "+", # inc
    "[", # loop
        ">>[-]<<", # reset next
        "[", # loop
            "-", # dec
            ">>", # move to next
            "+", # inc
            "<<", # move to cur
        "]",
        "+", # inc
        ">>", # go to next
        "-", #dec
    "]"
])
assert_prog(list_ready_prog)

"""
starts on space after element to write to
moves value on S to element
ends on S
"""

list_store_prog = "".join([
    "<", # go to E
    "[-]", # reset
    "<[<<]<", # go to S
    "[->>>[>>]<+<[<<]<]", # move value from S to element
])
assert_prog(list_store_prog)

"""
setup:
starts on space after element to retrive from
addmoves value from element to F and S
ends where it started
"""

list_fetch_prog = "".join([
    "<", # go to E
    "[", # loop
        "-", # dec
        "<", # go to to space between elements
        "[<<]", # go to 0 between S and F
        "<", # go to s
        "+", # inc
        ">>", # go to F
        "+", # inc
        ">[>>]<", # go to E
    "]>"
])
assert_prog(list_fetch_prog)


start = 17
reg_r1 = 1
reg_r2 = 3
reg_a = 5
reg_b = 7
reg_c = 9
reg_d = 11
reg_c0 = 13
reg_copy = 14
reg_const1 = 15
reg_const2 = 16
varpos = start
pos = 0
ln = 0
compiled = ""
variables = {}
lists = {}
statements = []

def assert_args(args, mn, mx = -1):
    if len(args) < mn or (mx != -1 and len(args) > mx):
        print(f"expected {mn} to {mx} arguments on line {ln}")
        exit()

def checkpos():
    global pos
    #should rest at 0, otherwise moving in loops might cause problems
    assert pos == 0

def parsenum(v):
    if len(v) == 2 and v[0] == "/":
        return ord(v[1])
    for c in v:
        if not c.isnumeric():
            return None
    n = int(v)
    return n if n >= 0 and n < 2**8 else None

def comp(program):
    global reg_a
    global compiled
    global ln
    global pos
    global variables
    global lists
    variables = {}
    lists = {}
    pos = 0
    for i in range(2, reg_c0, 2):
        setpos(i)
        inc(1)
    setpos(0)
    for line in program.split("\n"):
        ln += 1
        line = remove_comment(line)
        dat = line.strip().split()
        if len(dat) == 0:
            continue
        comp_command(dat[0], dat[1:])
    optimize()
    return compiled

def comp_command(cmd, args):
    global compiled
    global varpos
    global pos
    global statements
    if cmd == "var":
        assert_args(args, 1)
        # create a var with position varpos
        variables[args[0]] = varpos
        varpos += 1
    elif cmd == "lst":
        assert_args(args, 2)
        # create a list with position varpos
        lists[args[0]] = varpos
        varpos += int(args[1]) * 2 + 4
    elif cmd == "inp":
        assert_args(args, 1)
        setpos(get_reg(args[0]))
        compiled += ","
        setpos(0)
    elif cmd == "out":
        assert_args(args, 1)
        n = parsenum(args[0])
        if n == None:
            setpos(get_reg(args[0]))
        else:
            storeconst(reg_const1, n)
            setpos(reg_const1)
        compiled += "."
        setpos(0)
    elif cmd == "set":
        assert_args(args, 2)
        nm = parsenum(args[1])
        r = get_reg(args[0])
        if nm != None:
            storeconst(r, nm)
        else:
            copyval(get_reg(args[1]), [r])
    elif cmd == "add":
        assert_args(args, 2)
        nm = parsenum(args[1])
        r = get_reg(args[0])
        if nm != None:
            setpos(r)
            inc(nm)
            setpos(0)
        else:
            add(get_reg(args[1]), [r])
    elif cmd == "sub":
        assert_args(args, 2)
        nm = parsenum(args[1])
        r = get_reg(args[0])
        if nm != None:
            setpos(r)
            dec(nm)
            setpos(0)
        else:
            sub(get_reg(args[1]), [r])
    elif cmd == "loop":
        assert_args(args, 1)
        eval_statement(args[0])
        statements.append(args[0])
        setpos(reg_r1)
        compiled += "["
        setpos(0)
    elif cmd == "endloop":
        assert_args(args, 0)
        eval_statement(statements.pop())
        setpos(reg_r1)
        compiled += "]"
        setpos(0)
    elif cmd == "if":
        assert_args(args, 1)
        eval_statement(args[0])
        setpos(reg_r1)
        compiled += "["
        setpos(0)
    elif cmd == "endif":
        assert_args(args, 0)
        storeconst(reg_r1, 0)
        setpos(reg_r1)
        compiled += "]"
        setpos(0)
    # retrieve
    elif cmd == "ret":
        #reg, list, idx
        assert_args(args, 3)
        nm = parsenum(args[2])
        const_idx = nm != None
        idx = nm if const_idx else get_reg(args[2])
        get_from_list(get_list(args[1]), idx, get_reg(args[0]), const_idx)
    # store
    elif cmd == "sto":
        #val, list, idx
        assert_args(args, 3)
        val = parsenum(args[0])
        idx = parsenum(args[2])
        const_val = val != None
        const_idx = idx != None
        val = val if const_val else get_reg(args[0])
        idx = idx if const_idx else get_reg(args[2])
        store_to_list(get_list(args[1]), idx, val, const_idx, const_val)
    else:
        print(f"invalid command \"{cmd}\" on line {ln}")
        exit()
        

def get_from_list(lst, index, output_reg, const_index):
    global compiled
    if const_index:
        storeconst(lst + 3, index)
    else:
        copyval(index, [lst + 3])
    setpos(lst + 2)
    empty()
    setpos(lst)
    empty()
    compiled += ">>>" + list_ready_prog + list_fetch_prog + list_store_prog
    setpos(0)
    copyval(lst + 2, [output_reg])

def store_to_list(lst, index, value, const_index, const_value):
    global compiled
    global compiled
    if const_index:
        storeconst(lst + 3, index)
    else:
        copyval(index, [lst + 3])
    if const_value:
        storeconst(lst, value)
    else:
        copyval(value, [lst])
    setpos(lst)
    compiled += ">>>" + list_ready_prog + list_store_prog
    setpos(0)
    

def remove_comment(line):
    for i in range(len(line)):
        if line[i] == "#":
            return line[:i]
    return line

def get_list(lst):
    if not lst in lists:
        print(f"undefined list \"{lst}\" on line {ln}")
        exit()
    return lists[lst]

def get_reg(var):
    if not var in variables:
        print(f"undefined variable \"{var}\" on line {ln}")
        exit()
    return variables[var]

def setpos(n):
    global pos
    global compiled
    if pos < n:
        compiled += ">" * (n - pos)
    elif n < pos:
        compiled += "<" * (pos - n)
    pos = n
    
def empty():
    global compiled
    compiled += "[-]"

def emptyregs(regs):
    for reg in regs:
        setpos(reg)
        empty()

def moveval(frm, regs):
    checkpos()
    emptyregs(regs)
    setpos(0)
    addmove(frm, regs, False)

def addmove(frm, regs, sub):
    global compiled
    checkpos()
    setpos(frm)
    compiled += "["
    dec(1)
    # move value
    for reg in regs:
        setpos(reg)
        if sub:
            dec(1)
        else:
            inc(1)
    setpos(frm)
    compiled += "]"
    setpos(0)

def add(frm, regs):
    checkpos()
    setpos(reg_copy)
    empty()
    setpos(0)
    addmove(frm, regs + [reg_copy], False)
    addmove(reg_copy, [frm], False)

def sub(frm, regs):
    global compiled
    checkpos()
    setpos(frm)
    #compiled += "d."
    setpos(0)
    copyval(frm, [reg_a])
    setpos(frm)
    #compiled += "d."
    setpos(reg_a)
    #compiled += "d."
    setpos(0)
    addmove(reg_a, regs, True)

def copyval(frm, regs):
    #move frm to all regs and reg0
    moveval(frm, regs + [reg_copy])
    
    #move reg0 to frm
    moveval(reg_copy, [frm])

def inc(n):
    global compiled
    compiled += "+" * n

def dec(n):
    global compiled
    compiled += "-" * n

def storeconst(reg, v):
    global compiled
    checkpos()
    setpos(reg)
    empty()
    compiled += "+" * v
    setpos(0)

def optimize():
    global compiled
    old = ""
    while old != compiled:
        old = compiled
        compiled = compiled.replace("<>", "")
        compiled = compiled.replace("><", "")
        compiled = compiled.replace("+-", "")
        compiled = compiled.replace("-+", "")

def eval_statement(statement):
    for op in (">=", "=", ">"):
        sp = statement.split(op)
        if len(sp) == 2:
            n1 = parsenum(sp[0])
            n2 = parsenum(sp[1])
            r1 = None
            r2 = None
            if n1 != None:
                storeconst(reg_const1, n1)
                r1 = reg_const1
            else:
                r1 = get_reg(sp[0])
            if n2 != None:
                storeconst(reg_const2, n2)
                r2 = reg_const2
            else:
                r2 = get_reg(sp[1])
            compare(r1, r2, op)
            return
    print(f"invalid statement on line {ln}")
    exit()


def compare(reg1, reg2, op):
    global compiled
    # a and c will be the value of reg1
    copyval(reg1, [reg_a, reg_c])
    # b will be the value of reg2
    copyval(reg2, [reg_b])
    # c will be a + b
    add(reg2, [reg_c])
    # empty r1 and r2
    storeconst(reg_r1, 1)
    storeconst(reg_r2, 1)
    setpos(0)
    # run compare
    compiled += compare_prog
    # fix values
    if op == ">=":
        return
    elif op == "=":
        moveval(reg_r1, [reg_a])
        moveval(reg_r2, [reg_b])
        storeconst(reg_r1, 1)
        storeconst(reg_c, 2)
        compiled += and_prog
    elif op == ">":
        moveval(reg_r2, [reg_a])
        storeconst(reg_r1, 1)
        compiled += not_prog
    
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("supply 1 or 2 arguments")
    exit()
f = open(sys.argv[1], "r")
src = f.read()
f.close()
c = comp(src)
#print(ord(" "))
#print(compare_prog)
#c = comp(prgm)
#print("Compiled, will run following program:")
#print(len(c))
if len(sys.argv) == 2:
    brainfuck(c, False)
else:
    rf = open(sys.argv[2], "w")
    rf.write(c)
    rf.close()
