"""
  Decompiles bin files into a series of instructions.
"""

from synacor.vm import FileLoader, Decompiler

def main():
    data = FileLoader.load('memdump.dat')
    decompiler = Decompiler()
    decompiler.decompile(data)

if __name__ == "__main__":
    main()