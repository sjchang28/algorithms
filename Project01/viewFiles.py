import gzip
import re

def view_sdata(file):
    print("*** "+file)
    with gzip.open(file, 'rt', encoding="latin-1") as fin:
        arr = re.findall(r'2015.*\n', fin.read())
        for line in arr:
            strippedLine = line.strip("\n")
            print(strippedLine)
def view_data(file):
    print("*** "+file)
    with open(file,"rb+") as fin:
        lines = fin.readlines()
        for line in lines:
            print(line)

# Driver program to test above function
if __name__ == "__main__":
	view_data("/Users/stephenchang/Files/Projects/Microsoft VS Code/algorithms/Project01/out/mergesort/Run Time Complexity/logs/runtimes_B.bin")
