"""
  Decompiles bin files into a series of instructions.
"""

from synacor.vm import FileLoader, Decompiler

def main():
    data = FileLoader.load('challenge.bin')
    decompiler = Decompiler()
    decompiler.decompile(data)

if __name__ == "__main__":
    main()