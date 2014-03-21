"""
  Decompiles bin files into a series of instructions.
"""

from synacor import debugger

def main():
    data = debugger.FileLoader.load('challenge.bin')
    decompiler = debugger.Decompiler()
    decompiler.decompile(data)

if __name__ == "__main__":
    main()