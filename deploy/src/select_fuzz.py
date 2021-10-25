#python3 select_fuzz.py binary_name

from pwn import ELF
from capstone import *
from capstone.arm import *
import sys, os, random

def is_virtual(ins):
    branches=['bl', 'blx', 'bx'] #need to search virtual call
    if ins.mnemonic in branches:
        for i in ins.operanSds:
            reg = ins.reg_name(i.value.reg)
            if reg != 'lr' and (i.type != ARM_OP_IMM):
                return True

def is_syscall(ins):
    branches=['swi', 'svc'] #need to search
    if ins.mnemonic in branches:
        return True


def is_branch(ins):
    branches = ['bl', 'blx']
    if ins.mnemonic in branches:
        for i in ins.operands:
            if i.type == ARM_OP_IMM:     # we only consider imm.
                return i.value.imm
    return 0    # address 0 means its not a imm-branch



def DFS(md, addr, visited, depth, size, black, name, sys_list, parents):    
    indent = ' '*depth
    code = elf.read(addr, size)     # do something about each function size.
    visited.append(addr) #to check visited function
    print(indent+'visiting function %s, size %s'%(hex(addr), size))


    try:
        M = md.disasm(code, addr)
    except:
        print("bad opcode...") #check disassemble error
        return


    # list up all instructions in this function.
    for ins in M:
        ins_string = '{0} {1}'.format(ins.mnemonic, ins.op_str)
        print(indent+"0x%x:\t%s\t%s" %(ins.address, ins.mnemonic, ins.op_str))
        present_addr=ins.address


        if is_syscall(ins):
            print(indent+'syscall find')
            sys_list.append(addr) #add func addr to sys_call to patch later 
            black.append(addr) #add func addr to black 

            print("%s%s"%(indent,parents))
            #sys_list.extend(parents) #to show how many syscall in target binary
            black.extend(parents) #we cannot use function include syscall
            print(indent+'put parents to black')
        
            raise 1 #finish search -> go to next func
    

        if is_virtual(ins):
            print(indent+"it is virtual call!! in function addr %s, stop" %(hex(addr))) #print function addr
            black.append(addr) #add func addr to black

            print("%s%s"%(indent,parents))
            black.extend(parents) #we cannot use function include virtual call
            print(indent+'put parents to black')
            
            raise 1


        if is_branch(ins) != 0:
            #record parents
            #if we have func call opcode -> record parent function
            parents.append(addr)

            new_addr = is_branch(ins)
            if new_addr not in visited and new_addr not in black:
                try:
                    new_name=map[new_addr][0]
                    new_size=map[new_addr][2]
                    
                except:
                    invalid.append(new_addr)#we cannot branch to new_addr
                    black.append(addr) #add func addr that includes invalid
                    print(indent+'invalid func : not in binary')
                    print("%s%s"%(indent,parents))
                    black.extend(parents)
                    print(indent+'put parents to black')
                    raise 1 # go to big try part
                
                
                DFS(md, new_addr, visited, depth+1, new_size, black, new_name, sys_list, parents)
                
            elif new_addr in visited and new_addr not in black:
                #if new_addr only in visit list, pass only one branch line
                print(indent+'%s is already visited'%hex(new_addr))
                print(indent+'pop visited parents of visited')
                parents.pop() #normal finish, pop one parents

            else:
                print(indent+'cant branch to black, escape!')
                print("%s%s"%(indent,parents))
                black.extend(parents)
                print(indent+'put parents to black')
                raise 1 #stop all, go to big try part
    
    parents.pop() #normal finish, pop one parents
    print(indent+'normal return %s, pop parents' %(hex(addr)))


#start
filename=sys.argv[1]
elf = ELF(sys.argv[1])


#to make [name, addr, size] map
func_list=list(elf.functions.keys()) #funcname list
func_num=len(func_list)
map={}
for i in range(func_num):
    name=func_list[i]
    addr=elf.symbols[name]

    if addr%2==1:
        addr=addr-1

    size=elf.functions[name].size
    map[addr]=[name, addr, size]


#RUN ALL
black=[] #blacklist(vitual call, systemcall, invalid, and parents of them)
V=[] #visited check
sys_list=[] #systemcall
invalid=[] #invalid addr(cannot jump with pwntools and mode error)


for i in range(func_num):
    parents=[]

    name=func_list[i]
    addr=elf.symbols[name]
    size=elf.functions[name].size

    #check capstone mode from symbol addr
    if addr % 2 == 0:
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        print("\nARM")

    if addr %2 == 1:
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        addr = addr -1
        print("\nTHUMB")

    md.detail = True

    print("===============================")
    print("<%s, %s>" %(name, hex(addr)))

        #check for visit
    if (addr in V) or (addr in black) :
        print("**blacklist function or visited**:",hex(addr))
        print('')
        continue


    try:
        DFS(md, addr, V, 0, size, black, name, sys_list, parents)    # run DFS.
    except:
        pass



print("\n===================<%s binary report>=======================" %(filename))
V=set(V)
black=set(black)
sys_list=set(sys_list)
invalid=set(invalid)

print("visted num : %s" %len(V))
print("blacklist num(4 case):", len(black))
print("systemcall num:", len(sys_list))
print("invalid address num:", len(invalid))



temp=V-(black|sys_list|invalid) #black already include syscall
temp=list(temp)


print("\n***available functions*** :",len(temp))

for i in temp: 
    print("addr: %s, size: %s, name:%s" %(hex(i), map[i][2], map[i][0]))
    name=map[i][0]
    print("For wrapper.c-symbol addr of <%s>:%s\n" %(name, hex(elf.symbols[name])))
