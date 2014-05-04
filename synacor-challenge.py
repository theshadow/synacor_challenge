"""
    Entry point into the challenge code.
"""

import sys, os

from synacor.vm import Vm, VmDebugger, FileLoader

def main():
    """
    ADD @0, @1, 4
    OUT @0
    """
    data = FileLoader.load('challenge.bin')
    #data = numpy.array([9, 32768, 32769, 4, 19, 32768], dtype=numpy.uint16)

    vm = Vm()
    vm.load(data)
    #debugger.run()

    output_file = None
    if len(sys.argv) == 2:
        output_file = sys.argv[1]

    debugger = VmDebugger(vm, output_file=output_file)
    debugger.run()

if __name__ == "__main__":
    main()
