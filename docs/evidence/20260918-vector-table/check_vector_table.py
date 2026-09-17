import struct, sys
p = r"D:\Project\FreeRTOS Worksapce\demo\Debug\demo.elf"
d = open(p, "rb").read()
assert d[:4] == b"\x7fELF"
e_shoff = struct.unpack_from("<I", d, 0x20)[0]
e_shentsize = struct.unpack_from("<H", d, 0x2E)[0]
e_shnum = struct.unpack_from("<H", d, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", d, 0x32)[0]
def sec(i):
    off = e_shoff + i * e_shentsize
    name, typ, flags, addr, offset, size = struct.unpack_from("<IIIIII", d, off)
    return name, addr, offset, size
strtab_off = sec(e_shstrndx)[2]
def name_of(i):
    n, a, o, s = sec(i)
    end = d.index(b"\x00", strtab_off + n)
    return d[strtab_off + n:end].decode()
vec = None
for i in range(e_shnum):
    nm = name_of(i)
    if nm in (".isr_vector", ".vectors"):
        vec = sec(i)
        print("section", nm, "addr", hex(vec[1]), "fileoff", hex(vec[2]), "size", vec[3])
if vec:
    off = vec[2]
    ents = struct.unpack_from("<16I", d, off)
    labels = {0:"initial_SP",1:"Reset",2:"NMI",3:"HardFault",4:"MemManage",5:"BusFault",6:"UsageFault",11:"SVCall",12:"DebugMon",14:"PendSV",15:"SysTick"}
    for i, v in enumerate(ents):
        print(i, labels.get(i, "-"), hex(v))
