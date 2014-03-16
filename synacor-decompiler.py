"""
  Decompiles bin files into a series of instructions.
"""

from synacor import vm

def main():
    data = vm.FileLoader.load('challenge.bin')
    decompiler = vm.Decompiler()
    decompiler.decompile(data)

if __name__ == "__main__":
    main()