from pathlib import Path
import sys
import math

def design(inline):
    if len(inline) == 3:
        symbol, label, opcode = inline[0], inline[1], inline[2]
        return f"{symbol:<8}{label:<8}{opcode:<9}"
    elif len(inline) == 2:
        return f"{inline[0]:<8}{inline[1]:<8}"
# Ensure paths are provided as command-line arguments
if len(sys.argv) != 3:
    print("Usage: python pass1.py <input_file_path> <optab_file_path>")
    sys.exit(1)

# Get the file paths from command-line arguments
input_file_path = Path(sys.argv[1])
intermediate_file_path = Path("temp_files/intermediate.txt")
symtab_file_path = Path("temp_files/symtab.txt")
record_file_path = Path("temp_files/record.txt")
output_file_path = Path("temp_files/out.txt")

# Open the files using the provided paths
try:
    with input_file_path.open('r') as file1, \
         intermediate_file_path.open('w') as file2, \
         symtab_file_path.open('w') as file3, \
         record_file_path.open('a') as file4, \
         output_file_path.open('a') as file5:
        
        line1 = file1.readline()
        locctr = 0X0000  
        s = line1.split()
        flg=1
        if len(s)==1:
            file2.write(hex(locctr)[2:].zfill(4) + '\t' + s[0]+ '\tSTART\t' + '0000\n')
            flg=0
        if flg==1 and s[1] == 'START' :
            locctr = int(s[2], 16)
            start = locctr
            file2.write(hex(locctr)[2:].zfill(4) + '\t' + design(s)+'\n')

        for line in file1:
            s = line.split()
            if s[1] == 'END':
                file2.write(hex(locctr)[2:].zfill(4) + '\t' + design(s)+'\n')
                break

            file2.write(hex(locctr)[2:].zfill(4) + '\t' + design(s)+'\n')

            if s[0] != '**' and s[0] != '-':
                file3.write(s[0] + '\t' + hex(locctr) + '\n')

            if s[1] == 'RESW':
                locctr += 3 * int(s[2])
            elif s[1] == 'RESB':
                locctr += int(s[2])
            elif s[1] == 'WORD':
                locctr += 3
            elif s[1] == 'BYTE':
                if s[2][0] == 'X':
                    leng = (len(s[2]) - 3) / 2
                    locctr += math.ceil(leng)
                else:
                    leng = len(s[2]) - 3
                    locctr += leng
            else:
                locctr += 3

except Exception as e:
    error_message = f"Error has occurred: {str(e)}\n"
    
    with record_file_path.open('a') as file4, output_file_path.open('a') as file5:
        file4.write(error_message)
        file5.write(error_message)
