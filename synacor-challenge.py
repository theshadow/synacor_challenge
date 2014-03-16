"""
    Entry point into the challenge code.
"""

import numpy

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
    #vm.run()

    debugger = VmDebugger(vm)
    debugger.run()

if __name__ == "__main__":
    main()
