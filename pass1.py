def design(inline):
    if inline[0]=='**':
        return '\t\t'+inline[1]+'\t\t'+inline[2]+'\n'
    else:
        return inline[0]+'\t'+inline[1]+'\t'+inline[2]+'\n'
file1 = open('input.txt', 'r')
file2 = open('intermediate.txt', 'w')
file3 = open('symtab.txt','w')
line1 = file1.readline()
locctr = 0x0000  
s = line1.split()
if s[1] == 'START':
    locctr = int(s[2], 16)
    start = locctr
    file2.write(hex(locctr) + '\t' + line1)

else:
    locctr = 0
    start = 0
for line in file1:
    s = line.split()
    if s[1] == 'END':
        file2.write(hex(locctr) + '\t' + line)
        break
    file2.write(hex(locctr) + '\t' + line)
    if s[0] != '**':
        file3.write(s[0] + '\t' + hex(locctr) + '\n')
    if s[1] == 'RESW':
        locctr += 3 * int(s[2])
    elif s[1] == 'RESB':
        locctr += int(s[2])
    elif s[1] == 'WORD':
        locctr += 3
    elif s[1] == 'BYTE':
        leng=len(s[2])-3
        locctr += leng
    else:
        locctr += 3
    
