from pathlib import Path

def design(inline):
    location = inline[0].zfill(4)
    if len(inline) == 4:
        label, opcode, operand = inline[1], inline[2], inline[3]
        if inline[1]=='**' or inline[1]=='-':
            return f"{location:<8}{'':<8}{opcode:<8}{operand:<9}"
        elif inline[2]=='START':
            return f"{' ':<8}{label:<8}{opcode:<8}{operand:<9}"
        else:
            return f"{location:<8}{label:<8}{opcode:<8}{operand:<9}"
    elif len(inline) == 3:
        label, opcode = inline[1], inline[2]
        return f"{location:<8}{label:<8}{opcode:<9}"
    else:
        return f"{location:<8}{inline[1]:<8}{inline[2]:<9}"

TEMP_DIR = Path("temp_files")

input_file_path = TEMP_DIR / "input.txt"
intermediate_file_path = TEMP_DIR / "intermediate.txt"
symtab_file_path = TEMP_DIR / "symtab.txt"
optab_file_path = TEMP_DIR / "optab.txt"
output_file_path = TEMP_DIR / "record.txt"
record_file_path = TEMP_DIR / "out.txt"

def string_to_hex(string):
    hex_string = ''.join(format(ord(char), '02X') for char in string)
    return hex_string

symtab = {}
try:
    with open(symtab_file_path, 'r') as f:
        for line in f:
            label, address = line.split()
            if label in symtab:
                with open(record_file_path, 'a') as file3, open(output_file_path, 'a') as file4:
                    file3.write(f"Duplicate label: {label}\n")
                    file4.write(f"Duplicate label: {label}\n")
                break
            symtab[label] = address
except Exception:
    with open(record_file_path, 'a') as file3, open(output_file_path, 'a') as file4:
        file3.write("Error has occurred while reading symtab\n")
        file4.write("Error has occurred while reading symtab\n")

optab = {}
try:
    with open(optab_file_path, 'r') as f:
        for line in f:
            mnemonic, opcode = line.split()
            optab[mnemonic] = opcode
except Exception:
    with open(record_file_path, 'a') as file3, open(output_file_path, 'a') as file4:
        file3.write("Error has occurred while reading optab\n")
        file4.write("Error has occurred while reading optab\n")

try:
    with open(intermediate_file_path, 'r') as file2:
        add1 = file2.readline()
        st = add1.split()
        startadd_int = int(st[0], 16)
        last = file2.readlines()[-1]
        re = last.split()
        lastline_int = int(re[0], 16)
        diff = hex(lastline_int - startadd_int)
except Exception:
    with open(record_file_path, 'a') as file3, open(output_file_path, 'a') as file4:
        file3.write("Error has occurred while calculating program length\n")
        file4.write("Error has occurred while calculating program length\n")

Text = ''
tc = 0
stack = []
startadd = None
currentadd = None
stadd = None

def record(opc, locctr):
    global tc, startadd

    opc_length = len(opc) // 2

    if len(stack) == 0:
        startadd = locctr

    if len(stack) < 10:
        stack.append(opc)
        tc += opc_length
    else:
        Text = 'T^' + startadd.zfill(6) + '^' + hex(tc)[2:].zfill(2)
        for i in stack:
            Text += i
        with open(output_file_path, 'a') as file4:
            file4.write(Text.upper() + '\n')

        stack.clear()
        tc = opc_length
        startadd = locctr
        stack.append(opc)

try:
    flg=0
    with open(intermediate_file_path, 'r') as file2, \
         open(output_file_path, 'w') as file4, \
         open(record_file_path, 'w') as file3:

        file3.write(f"{'Loc':<8}{'Label':<8}{'Opcode':<8}{'Operand':<10}{'Code':<8}\n")
        file3.write('-' * 40 + '\n')

        for line in file2:
            s = line.split()
            currentadd = s[0]
            if s[2] == 'START':
                startadd = s[3]
                stadd = startadd
                file3.write(design(s)+'\n')
                file4.write('H^' + s[1] + '^00' + s[3].zfill(4) + '^' + diff[2:].zfill(6) + '\n')
                flg=1
            else:
                if flg==0:
                    file4.write('H^' + s[1] + '^00' + s[0].zfill(4) + '^' + diff[2:].zfill(6) + '\n')
                    stadd = s[0].zfill(6)
                    flg=1
                if s[2] in ['RESW', 'RESB', 'RESD', 'END']:
                    if len(stack) > 0:
                        Text = 'T^' + startadd.zfill(6) + '^' + hex(tc)[2:].zfill(2)
                        for i in stack:
                            Text += i
                        file4.write(Text.upper() + '\n')
                        stack.clear()
                        tc = 0
                    file3.write(design(s)+'\n')
                elif s[2] == 'WORD':
                    file3.write(design(s) +' '+ f"{hex(int(s[3]))[2:].zfill(6):<8}\n")
                    record('^' + hex(int(s[3]))[2:].zfill(6), currentadd)
                elif s[2] == 'BYTE':
                    file3.write(design(s) +' ' + f"{string_to_hex(s[3][2:len(s[3])-1]):<8}\n")
                    record('^' + string_to_hex(s[3][2:len(s[3])-1]), currentadd)
                else:
                    if s[2] in optab and s[2] != 'RSUB':
                        file3.write(design(s) + f" {optab[s[2]]:<2}{symtab[s[3]].zfill(4):<8}\n")
                        temp = '^' + optab[s[2]] + symtab[s[3]].zfill(4)
                        record(temp, currentadd)
                    else:
                        file3.write(f"{s[0].zfill(4):<16}{s[2]:<8} {'  ':<8} {optab[s[2]]:<2}0000\n")
                        temp = '^' + optab[s[2]] + '0000'
                        record(temp, currentadd)

        if len(stack) > 0:
            Text = 'T^' + startadd.zfill(6) + '^' + hex(tc)[2:].zfill(2)
            for i in stack:
                Text += i
            file4.write(Text.upper() + '\n')

        file4.write('E^00' + stadd.zfill(4) + '\n')

except Exception:
    with open(record_file_path, 'a') as file3, open(output_file_path, 'a') as file4:
        file3.write("Error has occurred during intermediate file processing\n")
        file4.write("Error has occurred during intermediate file processing\n")
