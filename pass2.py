symtab = {}
with open('symtab.txt', 'r') as f:
    for line in f:
        label, address = line.split()
        if label in symtab:
            print(f"Duplicate label: {label}")
            break
        symtab[label] = address

optab = {}
with open('optab.txt', 'r') as f:
    for line in f:
        mnemonic, opcode = line.split()
        optab[mnemonic] = opcode

def string_to_hex(string):
    # Convert each character in the string to its hexadecimal ASCII value
    hex_string = ''.join(format(ord(char), '02X') for char in string)
    return hex_string

file2 = open('intermediate.txt', 'r')
add1=file2.readline()
st=add1.split()
startadd_int = int(st[0], 16)
last=file2.readlines()[-1]
re=last.split()
lastline_int = int(re[0], 16)
diff =hex(lastline_int - startadd_int)


file2.close()
file2 = open('intermediate.txt', 'r')
file3 = open('out.txt', 'w')
file4 = open('record.txt', 'w')
# Initialize necessary variables
Text = ''
tc = 0  # Text record length in bytes (total length of object codes)
stack = []
startadd = None  # Start address for each text record
currentadd = None  # Current address being processed
stadd= None

def record(opc, locctr):
    global tc, startadd

    # Calculate the length of this object code in bytes (each character is half a byte)
    opc_length = len(opc) // 2

    if len(stack) == 0:  # New text record
        startadd = locctr  # Start address of the new record

    # Add object code to the stack if we have space for another record
    if len(stack) < 10:  # Can hold at most 10 object codes
        stack.append(opc)
        tc += opc_length
    else:
        # Write the text record to the file
        Text = 'T^' + startadd.zfill(6) + '^' + hex(tc)[2:].zfill(2)
        for i in stack:
            Text += i
        file4.write(Text.upper() + '\n')

        # Reset for a new text record
        stack.clear()
        tc = opc_length
        startadd = locctr
        stack.append(opc)

# Process each line from the intermediate file
for line in file2:
    s = line.split()
    currentadd = s[0]  # Location counter from the intermediate file

    if s[2] == 'START':
        startadd = s[3]  # Start address for the program
        stadd=startadd
        file3.write(line)  # Keep the line as is
        file4.write('H^' + s[1]+ '^00' + s[3] +'^'+ diff[2:] +'\n')
    else:
        if s[2] == 'RESW' or s[2] == 'RESB' or s[2]=='RESD' or  s[2] == 'END':
            # Before handling RESW/RESB, write any remaining records to the file
            if len(stack) > 0:
                # Write the last text record
                Text = 'T^' + startadd.zfill(6) + '^' + hex(tc)[2:].zfill(2)
                for i in stack:
                    Text += i
                file4.write(Text.upper() + '\n')
                stack.clear()
                tc = 0
            file3.write(line)  # Keep the line as is
        elif s[2] == 'WORD':
            file3.write(line.strip() + ' 00000' + s[3] + '\n')
            record('^'+'00000' + s[3], currentadd)
        elif s[2] == 'BYTE':
            file3.write(line.strip() + ' ' + string_to_hex(s[3][2:len(s[3])-1])+ '\n')
            record('^'+ string_to_hex(s[3][2:len(s[3])-1]), currentadd)
        else:
            if s[2] in optab and s[2]!='RSUB':
                file3.write(line.strip() + ' ' + optab[s[2]] + symtab[s[3]][2:] + '\n')
                temp = '^'+optab[s[2]] + symtab[s[3]][2:]
                record(temp, currentadd)
            else:
                file3.write(line.strip() + ' ' + optab[s[2]] + '0000\n')
                temp = '^'+optab[s[2]] + '0000'
                record(temp, currentadd)

# Write the final text record if anything remains in the stack
if len(stack) > 0:
    Text = 'T^' + startadd.zfill(6) + '^' + hex(tc)[2:].zfill(2) + '^'
    for i in stack:
        Text += i
    file4.write(Text.upper() + '\n')

# Write the End record
file4.write('E^00' + stadd+ '\n')

file2.close()
file3.close()
file4.close()
