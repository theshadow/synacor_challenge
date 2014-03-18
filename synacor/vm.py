"""
    VM library that contains the bulk of the VM code.
"""

import sys

import numpy
from numpy import array, uint16

from pubsub import PublisherAware, PubSub

INSTRUCTIONS = {
    0: 'halt',
    1: 'set',
    2: 'push',
    3: 'pop',
    4: 'eq',
    5: 'gt',
    6: 'jmp',
    7: 'jt',
    8: 'jf',
    9: 'add',
    10: 'mult',
    11: 'mod',
    12: 'and',
    13: 'or',
    14: 'not',
    15: 'rmem',
    16: 'wmem',
    17: 'call',
    18: 'ret',
    19: 'out',
    20: 'in',
    21: 'noop'
}

HALT = 0   # stop       - execution and terminate the program
SET = 1    # set a b    - set register <a> to value of <b>
PUSH = 2   # push a     - push <a> onto the stack
POP = 3    # pop a      - remove the top element from the stack and write it into <a>; empty stack = error
EQ = 4     # eq a b c   - set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
GT = 5     # gt a b c   - set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
JMP = 6    # jmp a      - Jump to <a>
JT = 7     # jt a b     - if <a> is nonzero, jump to <b>
JF = 8     # jf a b     - if <a> is zero, jump to <b>
ADD = 9    # add a b c  - store into <a> the sum of <b> and <c> (modulo 32768)
MULT = 10  # mult a b c - store into <a> the product of <b> and <c> (modulo 32768)
MOD = 11   # mod a b c  - store into <a> the remainder of <b> divided by <c>
AND = 12   # and a b c  - store into <a> the bitwise AND of <b> and <c>
OR = 13    # or a b c   - store into <a> the bitwise OR of <b> and <c>
NOT = 14   # not a b    - store into <a> 15-bit bitwise inverse of <b>
RMEM = 15  # rmem a b   - read memory at address <b> and write it to <a>
WMEM = 16  # wmem a b   - write the value from <b> into memory at address <a>
CALL = 17  # call a     - write the address of the next instruction to the stack and jump to <a>
RET = 18   # ret        - remove the top element from the stack and jump to it; empty stack = halt
OUT = 19   # out a      - write the character represented by asci code <a> to the terminal
IN = 20    # in a       - read a character from the terminal and write its ascii code to <a>; assume continues till
           #              newline
NOOP = 21  # noop       - no operation

REGISTER_0 = 32768
REGISTER_1 = 32769
REGISTER_2 = 32770
REGISTER_3 = 32771
REGISTER_4 = 32772
REGISTER_5 = 32773
REGISTER_6 = 32774
REGISTER_7 = 32775

FIFTEENTH_BIT_MASK = uint16(~(1 << 15))

MAX_INT = 32768
MAX_VALID_VALUE = 32775
MAX_MEMORY_ADDRESS = 32767
TOROIDAL_MEMORY = True


class Decompiler(object):

    ZERO_OPTS = [HALT, NOOP, RET]
    ONE_OPTS = [PUSH, POP, JMP, CALL, OUT, IN]
    TWO_OPTS = [SET, JT, JF, RMEM, WMEM, NOT]
    THREE_OPTS = [EQ, GT, ADD, MULT, MOD, AND, OR]

    def __init__(self):
        self.line = 0
        self.offset = 0

    def decompile(self, data):
        a = b = c = None

        while True:
            if self.offset > len(data) - 1:
                break

            self.offset = self.decompile_offset(self.offset, data)

            self.line += 1

    def decompile_offset(self, offset, data):
        instruction = data[offset]

        if instruction in Decompiler.ZERO_OPTS:
            self.print_instruction(offset, instruction)
            offset += 1
        elif instruction in Decompiler.ONE_OPTS:
            a = data[offset + 1]
            self.print_instruction(offset, instruction, a)
            offset += 2
        elif instruction in Decompiler.TWO_OPTS:
            a = data[offset + 1]
            b = data[offset + 2]
            self.print_instruction(offset, instruction, a, b)
            offset += 3
        elif instruction in Decompiler.THREE_OPTS:
            a = data[offset + 1]
            b = data[offset + 2]
            c = data[offset + 3]
            self.print_instruction(offset, instruction, a, b, c)
            offset += 4
        else:
            print "Unknown instruction: %s:%s" % (str(offset), str(instruction))
            offset += 1

        return offset

    def print_instruction(self, offset, instruction, a=None, b=None, c=None):
        params = [self.parse_argument(x)  for x in [a, b, c] if x is not None]
        param_tokens = [] + (["%s"] * len(params))

        line = "[" + str(self.line).zfill(5) + ":" + str(offset).zfill(5) + "]: " + INSTRUCTIONS[instruction] \
               + " " + ", ".join(param_tokens)

        print line % tuple(params)

    def parse_argument(self, argument):
        if Vm.is_register(argument):
            return "@" + str(VmDebugger.INVERSE_REGISTER_MAP[argument])
        return str(argument)


class FileLoader(object):
    @staticmethod
    def load(file):
        data = numpy.fromfile(file, dtype=uint16)
        return data

    @staticmethod
    def save(ndarray, file):
        ndarray.astype('uint16').tofile(file)


class VmDebugger(object):
    """A debugger for the VM
    It works using a pubsub pattern, listening for when the VM emits specific events allowing the user to step through
    code
    """

    REGISTER_ANNOTATION = '@'

    COMMANDS = {
        'continue': 'c',
        'peek': 'k',
        'poke': 'o',
        'push': 'u',
        'pop': 'p',
        'speek': 'e',
        'spoke': 't',
        'jump': 'j',
        'set': 's',
        'registers': 'r',
        'resume': 'l',
        'quit': 'q',
        'spy': 'n',
        'breaks': 'z',
        'save': 'm',
        'load': 'd',
        'breako': 'g',
        'ssize': 'Z',
        'stack': 'S',
        'cstack': 'C'
    }

    COMMAND_OPTS_COUNT = {
        'continue': 0,
        'peek': (1, 2),
        'poke': 2,
        'push': 1,
        'pop': 0,
        'speek': (1, 2),
        'spoke': 2,
        'jump': 1,
        'set': 2,
        'registers': 0,
        'resume': 0,
        'quit': 0,
        'spy': 0,
        'breaks': 1,
        'save': 1,
        'load': 1,
        'breako': 1,
        'ssize': 0,
        'stack': 0,
        'cstack': 0
    }

    COMMAND_SHORTCUTS = {v: k for k, v in COMMANDS.items()}

    REGISTER_MAP = {
        0: REGISTER_0,
        1: REGISTER_1,
        2: REGISTER_2,
        3: REGISTER_3,
        4: REGISTER_4,
        5: REGISTER_5,
        6: REGISTER_6,
        7: REGISTER_7,
    }

    INVERSE_REGISTER_MAP = {v: k for k, v in REGISTER_MAP.items()}

    @property
    def pubsub(self):
        if self._pubsub is None:
            self._pubsub = PubSub()
        return self._pubsub

    @pubsub.setter
    def pubsub(self, pubsub):
        self._pusbsub = pubsub

    @property
    def vm(self):
        return self._vm

    @vm.setter
    def vm(self, vm):
        self._vm = vm

    @property
    def decompiler(self):
        if self._decompiler is None:
            self._decompiler = Decompiler()
        return self._decompiler

    @decompiler.setter
    def decompiler(self, decompiler):
        self._decompiler = decompiler

    def __init__(self, vm):
        self._pubsub = None
        self._vm = None
        self.step_counter = 0
        self.step_continue = False
        self.resume = False
        self.spy = False
        self.break_step_count = None
        self.break_offset = None
        self._decompiler = None
        self.call_stack = numpy.array([], dtype='<u2')

        publisher = self.pubsub.new_publisher()
        vm.publisher = publisher

        self.vm = vm

        self.pubsub.subscribe('run-start', self.run_start)
        self.pubsub.subscribe('step', self.step)
        self.pubsub.subscribe('run-end', self.run_end)

    def run(self):
        self.vm.run()

    def run_start(self, vm):
        pass

    def run_end(self, vm):
        pass

    def step(self, vm):
        self.step_counter += 1

        if self.step_counter == self.break_step_count or self.vm.exec_ptr == self.break_offset:
            self.resume = False

        if self.spy:
            print "%s:%s - %s" % (str(self.step_counter),
                                  self.format_memory_address(self.vm.exec_ptr),
                                  INSTRUCTIONS[self.vm.read_memory(self.vm.exec_ptr)])

        self.call_stack = numpy.append(self.call_stack, self.vm.exec_ptr)

        if self.resume:
            return

        while not self.step_continue:
            user_input = self.get_input()
            self.parse_input(user_input)
        self.step_continue = False

    def get_input(self):
        user_input = raw_input("[%s:%s]> " % (str(self.step_counter),
                                              self.format_memory_address(self.vm.exec_ptr)))
        return user_input

    def parse_input(self, user_input):
        """ Breaks down the input into tokens so that it can be executed
        :param str user_input: The input from the terminal
        """
        if len(user_input) == 0:
            return

        tokens = user_input.strip().split(' ')
        command = tokens[0]
        options = tokens[1:]

        if len(command) == 1 and command in VmDebugger.COMMAND_SHORTCUTS:
            command = VmDebugger.COMMAND_SHORTCUTS[command]

        if command not in VmDebugger.COMMANDS:
            print "Command %s unknown, ignoring" % (command)
            return

        command_opts_count = self.COMMAND_OPTS_COUNT[command]
        correct_opt_count = False

        if len(options) == command_opts_count:
            correct_opt_count = True
        elif isinstance(command_opts_count, tuple) and len(options) in command_opts_count:
            correct_opt_count = True

        if not correct_opt_count:
            print "Invalid options count for %s" % (command)
            return

        getattr(self,'command_' + command)(*options)

    def command_ssize(self):
        """ Output the current size of the stack
        """
        print "Stack size: %s" % (str(len(self.vm.stack)))

    def command_stack(self):
        """ Output the stack
        """
        print self.vm.stack

    def command_cstack(self):
        """ Output the call stack
        """
        for memory_offset in self.call_stack:
            self.decompiler.decompile_offset(memory_offset, self.vm.memory)

    def command_breaks(self, step_count):
        """ Sets a break point at a specific step count
        """
        self.break_step_count = int(step_count)

    def command_breako(self, offset):
        """ Sets a break point at a specific execution offset
        """
        self.break_offset = int(offset)

    def command_save(self, filename):
        FileLoader.save(self.vm.memory, filename)

    def command_load(self, filename):
        self.vm.load(FileLoader.load(filename))

    def command_resume(self):
        self.resume = True
        self.step_continue = True

    def command_spy(self):
        self.spy = True

    def command_continue(self):
        """ Just allows the vm to continue to the next step
        """
        self.step_continue = True

    def command_peek(self, address_from, address_to=None):
        if address_from is None:
            print "Invalid address_from specified: " + self.format_memory_address(address_from)

        if address_to is not None:
            self.print_memory_range(address_from, address_to)
        else:
            self.print_memory_address(address_from)

    def command_poke(self, address, value):
        value = self.parse_register_annotation(value)

        address = int(address)
        value = uint16(value)

        if address < 0 or address > MAX_MEMORY_ADDRESS:
            print "Invalid memory address to poke, must be between 0...%s" % (str(MAX_MEMORY_ADDRESS))
            return

        if value > MAX_VALID_VALUE:
            print "Invalid value, must be between 0...%s" % (str(MAX_VALID_VALUE))
            return

        self.vm.write_memory(address, value)

    def command_speek(self, offset_from, offset_to=None):
        if len(self.vm.stack) == 0:
            print "Stack is empty."
            return

        if offset_from is None:
            print "Invalid offset_from specified: " + str(offset_from)

        stack_size = len(self.vm.stack)

        if offset_to is not None:
            self.print_stack_range(offset_from, offset_to)
        else:
            self.print_stack_offset(offset_from)

    def command_spoke(self, offset, value):
        value = self.parse_register_annotation(value)

        offset = int(offset)
        value = uint16(value)

        if value > MAX_VALID_VALUE:
            print "Invalid value, must be between 0...%s" % (str(MAX_VALID_VALUE))

        self.vm.write_stack(offset, value)

    def command_push(self, value):
        value = self.parse_register_annotation(value)
        value = uint16(value)
        self.vm.stack_push(value)

    def command_pop(self):
        value = self.vm.stack_pop()

        print "%s" % str(value)

    def command_jump(self, address):
        address = int(address)
        if address < 0 or address > MAX_MEMORY_ADDRESS:
            "Invalid point in memory to jump to, must be between 0...%s: %s" % (str(address), str(MAX_MEMORY_ADDRESS))

        self.vm.exec_ptr = address

    def command_set(self, register, value):
        register = self.parse_register_annotation(register)
        value = uint16(value)
        self.vm.set_register(register, value)

    def command_registers(self):
        registers = {}
        for offset in range(len(self.vm.registers)):
            value = self.vm.registers[offset]
            registers["@%s" % str(offset)] = value
        print registers

    def command_quit(self):
        self.step_continue = True
        self.vm.halt = True

    def print_memory_range(self, address_from, address_to):
        address_from = int(address_from)
        address_to = int(address_to)

        for address in range(address_from, address_to):
            self.print_memory_address(address)

    def print_memory_address(self, address):
        address = int(address)
        memory_value = self.vm.read_memory(address)
        memory_value = self.compose_register_annotation(memory_value)
        print "%s: %s" % (self.format_memory_address(address), memory_value)

    def print_stack_range(self, offset_from, offset_to):
        offset_from = int(offset_from)
        offset_to = int(offset_to)

        for offset in range(offset_from, offset_to):
            self.print_stack_offset(offset)

    def print_stack_offset(self, offset):
        offset = int(offset)
        stack_value = self.vm.read_stack(offset)
        stack_value = self.compose_register_annotation(stack_value)
        print "%s: %s" % (offset, stack_value)

    def parse_register_annotation(self, annotation):
        if annotation[0] == VmDebugger.REGISTER_ANNOTATION:
            annotation = VmDebugger.REGISTER_MAP[int(annotation[1])]
        return annotation

    def compose_register_annotation(self, value):
        value = uint16(value)
        if Vm.is_register(value):
            value = "@%s" % (str(VmDebugger.INVERSE_REGISTER_MAP[value]))

        return str(value)

    def format_memory_address(self, value):
        if not isinstance(value, str):
            value = str(value)
        return value.zfill(5)



class Vm(PublisherAware):
    """ A virtual machine with 21 instructions, 8 registers, 1 execution pointer, 15-bit addressable memory for uint16
    """

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, data):
        self._memory = data

    @property
    def stack(self):
        return self._stack

    @stack.setter
    def stack(self, stack):
        self._stack = stack

    @property
    def registers(self):
        return self._registers

    @registers.setter
    def registers(self, registers):
        self._registers = registers

    @property
    def exec_ptr(self):
        return self._exec_ptr

    @exec_ptr.setter
    def exec_ptr(self, value):
        self._exec_ptr = value

    def __init__(self):
        super(Vm, self).__init__()

        self.halt = False
        self._memory = numpy.zeros((MAX_MEMORY_ADDRESS,), dtype=numpy.dtype('<u2'))
        self._stack = array([], dtype=uint16)
        self._registers = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ]

        self._exec_ptr = 0

    def run(self):
        """ Executes the program loaded into memory one instruction at a time.
        """

        self.publisher.publish('run-start', vm=self)

        self.halt = False

        while not self.halt:
            self.publisher.publish('step', vm=self)

            if self.exec_ptr > (len(self.memory) - 1):
                raise OverflowError("Execution pointer has overran memory: " + str(self.exec_ptr))

            a = b = c = None

            instruction = self.memory[self.exec_ptr]

            if instruction == HALT:
                self.halt = True
                continue
            elif instruction == SET:
                a = self.get_a_param()
                b = self.get_b_param()

                assert isinstance(b, uint16)
                self.instruction_set(a, b)

                self.exec_ptr += 3
            elif instruction == PUSH:
                a = self.get_a_param()

                self.instruction_push(a)
                self.exec_ptr += 2
            elif instruction == POP:
                a = self.get_a_param()

                self.instruction_pop(a)

                self.exec_ptr += 2
            elif instruction == EQ:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_eq(a, b, c)

                self.exec_ptr += 4
            elif instruction == GT:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_gt(a, b, c)

                self.exec_ptr += 4
            elif instruction == JMP:
                a = self.get_a_param()

                self.instruction_jmp(a)
            elif instruction == JT:
                a = self.get_a_param()
                b = self.get_b_param()

                self.instruction_jt(a, b)
            elif instruction == JF:
                a = self.get_a_param()
                b = self.get_b_param()

                self.instruction_jf(a, b)
            elif instruction == ADD:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_add(a, b, c)

                self.exec_ptr += 4
            elif instruction == MULT:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_mult(a, b, c)

                self.exec_ptr += 4
            elif instruction == MOD:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_mod(a, b, c)

                self.exec_ptr += 4
            elif instruction == AND:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_and(a, b, c)

                self.exec_ptr += 4
            elif instruction == OR:
                a = self.get_a_param()
                b = self.get_b_param()
                c = self.get_c_param()

                self.instruction_or(a, b, c)

                self.exec_ptr += 4
            elif instruction == NOT:
                a = self.get_a_param()
                b = self.get_b_param()

                self.instruction_not(a, b)

                self.exec_ptr += 3
            elif instruction == RMEM:
                a = self.get_a_param()
                b = self.get_b_param()

                self.instruction_rmem(a, b)

                self.exec_ptr += 3
            elif instruction == WMEM:
                a = self.get_a_param()
                b = self.get_b_param()

                self.instruction_wmem(a, b)

                self.exec_ptr += 3
            elif instruction == CALL:
                a = self.get_a_param()

                self.instruction_call(a)
            elif instruction == RET:
                self.instruction_ret()
            elif instruction == OUT:
                a = self.get_a_param()

                self.instruction_out(a)

                self.exec_ptr += 2
            elif instruction == IN:
                a = self.get_a_param()

                self.instruction_in(a)

                self.exec_ptr += 2
            elif instruction == NOOP:
                self.exec_ptr += 1
                continue
            else:
                raise ValueError("Unknown instruction " + str(instruction))

        self.publisher.publish('run-end', vm=self)

    def load(self, data):
        """ Takes in parsed binary data and loads it into memory
        :param data: An array([], dtype=uint16) set of data.
        """
        if len(data) == 0:
            raise ValueError("No data to load")
        elif len(data) > MAX_MEMORY_ADDRESS + 1:
            raise OverflowError("Not enough memory to load program.")

        self.halt = False
        self.memory = numpy.append(data, numpy.zeros((MAX_MEMORY_ADDRESS - len(data),), dtype=numpy.dtype('<u2')))
        self.registers = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ]
        self.exec_ptr = 0

    # instruction methods

    def instruction_set(self, register, source):
        """ Set the register with the value from source, if source is a register the value will be read first.
        :param register: The register to store the value in
        :param source: The source/value to store in the register.
        """
        if Vm.is_register(source):
            source = self.get_register(source)

        self.set_register(register, source)

    def instruction_push(self, value):
        """ Pushes the passed in value onto the stack
        :param value: The value to push on to the stack if the value references a register it will read the value first.
        """
        if Vm.is_register(value):
            value = self.get_register(value)

        self.stack_push(value)

    def instruction_pop(self, destination):
        """ Pop a value from the stack and store it in the passed in destination
        :param destination: The place to store the value popped from the stack
        :raises ValueError if the stack is empty
        """
        if len(self.stack) == 0:
            raise ValueError("Attempted to POP against empty stack")

        value = self.stack_pop()
        self.set_register(destination, value)

    def instruction_eq(self, register, left_hand, right_hand):
        """ Sets register to 1 if left_hand is equal to right_hand; sets it to 0 otherwise.
        :param register: The register to set
        :param left_hand: The left hand of the equality operation
        :param right_hand: The right hand of the equality operation
        """
        self.set_register(register, 0)

        if Vm.is_register(left_hand):
            left_hand = self.get_register(left_hand)

        if Vm.is_register(right_hand):
            right_hand = self.get_register(right_hand)

        if left_hand == right_hand:
            self.set_register(register, 1)

    def instruction_gt(self, register, left_hand, right_hand):
        """ Set register to be 1 if the left_hand is greater than the right_hand
        :param register: The Register to set
        :param left_hand: The left hand side of the comparison operation
        :param right_hand: The right hand of the comparison operation
        """
        self.set_register(register, 0)

        if Vm.is_register(left_hand):
            left_hand = self.get_register(left_hand)

        if Vm.is_register(right_hand):
            right_hand = self.get_register(right_hand)

        if left_hand > right_hand:
            self.set_register(register, 1)

    def instruction_jmp(self, address):
        """ Jump to address in memory
        :param address: The memory address to jump to
        """
        self.exec_ptr = Vm.filter_mem_address(address)

    def instruction_jt(self, value, address):
        """ Jump to b if value is non-zero
        :param value: The value to check if it's non-zero
        :param address: The memory address to jump to
        """
        if Vm.is_register(value):
            value = self.get_register(value)

        if value > 0:
            self.exec_ptr = Vm.filter_mem_address(address)
        else:
            self.exec_ptr += 3

    def instruction_jf(self, value, address):
        """ Jump to b if value is zero
        :param value: The value to check if it's zero
        :param address: The memory address to jump to
        """
        if Vm.is_register(value):
            value = self.get_register(value)

        if value == 0:
            self.exec_ptr = Vm.filter_mem_address(address)
        else:
            self.exec_ptr += 3

    def instruction_add(self, register, a, b):
        """ Store into destination the sum of a and b
        :param register: The register to store the result to
        :param a: The left hand of the summation
        :param b: The right hand of the summation
        """
        if Vm.is_register(a):
            a = self.get_register(a)

        if Vm.is_register(b):
            b = self.get_register(b)

        result = ((a + b) % MAX_INT)

        self.set_register(register, ((a + b) % MAX_INT))

    def instruction_mult(self, register, a, b):
        """ Store into destination the product of a and b
        :param register: The register to store the result to
        :param a: The left hand of the product
        :param b: The right hand of the product
        """
        if Vm.is_register(a):
            a = self.get_register(a)

        if Vm.is_register(b):
            b = self.get_register(b)

        a = int(a)  # cast them to 32-bit integers so we can do maths with big numbers then modulus them.
        b = int(b)  #

        result = uint16((a * b) % MAX_INT)

        self.set_register(register, result)

    def instruction_mod(self, register, a, b):
        """ Store into destination the modulus of a and b
        :param register: The register to store the result to
        :param a: The left hand of the modulus
        :param b: The right hand of the modulus
        """
        if Vm.is_register(a):
            a = self.get_register(a)

        if Vm.is_register(b):
            b = self.get_register(b)

        self.set_register(register, (a % b) % MAX_INT)

    def instruction_and(self, register, a, b):
        """ Store into destination the bitwise and of a and b
        :param register: The register to store the result to
        :param a: The left hand of the bitwise and
        :param b: The right hand of the bitwise and
        """
        if Vm.is_register(a):
            a = self.get_register(a)

        if Vm.is_register(b):
            b = self.get_register(b)

        self.set_register(register, (a & b) & FIFTEENTH_BIT_MASK)

    def instruction_or(self, register, a, b):
        """ Store into destination the bitwise or of a and b
        :param register: The register to store the result to
        :param a: The left hand of the bitwise or
        :param b: The right hand of the bitwise or
        """
        if Vm.is_register(a):
            a = self.get_register(a)

        if Vm.is_register(b):
            b = self.get_register(b)

        self.set_register(register, (a | b) & FIFTEENTH_BIT_MASK)

    def instruction_not(self, register, value):
        """ Store into destination the bitwise not of a
        :param register: The register to store the result to
        :param value: The value to perform the bitwise not (inverse)
        """
        if Vm.is_register(value):
            value = self.get_register(value)

        # do the inverse and flip bit 16
        self.set_register(register, ~value & FIFTEENTH_BIT_MASK)

    def instruction_rmem(self, register, address):
        """ Read memory at address source and write it to destination
        :param register: The register to store the value in.
        :param address: The memory address to read from
        """

        if Vm.is_register(address):
            address = self.get_register(address)

        value = self.memory[Vm.filter_mem_address(address)]
        self.set_register(register, value)

    def instruction_wmem(self, address, value):
        """ Write the value stored in register to the memory address
        :param address: The memory address to write to.
        :param value: The register to read from
        """

        if Vm.is_register(address):
            address = self.get_register(address)

        if Vm.is_register(value):
            value = value = self.get_register(value)

        self.memory[Vm.filter_mem_address(address)] = value

    def instruction_call(self, address):
        """ Push the memory address of the next instruction onto the stack and then jump to address
        :param address: The memory address to jump to after pushing onto the stack
        """
        next_instruction_offset = self.exec_ptr + 2  # the value of the next instruction's memory

        self.stack_push(next_instruction_offset)

        if Vm.is_register(address):
            address = self.get_register(address)

        self.exec_ptr = Vm.filter_mem_address(address)

    def instruction_ret(self):
        """ Pop the top element off the stack and jump to it.
        """
        if len(self.stack) == 0:
            self.halt = True
            return

        address = self.stack_pop()

        if Vm.is_register(address):
            address = self.get_register(address)

        self.exec_ptr = Vm.filter_mem_address(address)

    def instruction_out(self, value):
        """ Output the ASCII character of value
        :param value: The value to print out, will read from register if it's a register value.
        """
        if Vm.is_register(value):
            value = self.get_register(value)
        sys.stdout.write(chr(value))

    def instruction_in(self, register):
        """ Accept input from the user, able to read in one character though will accept until newline.
        :param register: Where to store the ASCII value of the first character
        """
        user_input = raw_input('Input: ')

        value = uint16(ord(user_input[0]))
        self.set_register(register, value)

    #state modifying methods

    def set_register(self, register, value):
        """ Set the passed in register to the passed in value
        :param register: Register value
        :param value: Value to store in the register
        """
        if not Vm.is_register(register):
            raise ValueError("Expected register value, instead got: " + str(register))

        self.registers[(register - REGISTER_0)] = value

    def get_register(self, register):
        """Returns the value set in the register if the passed in value isn't a valid register it raises a ValueError
        :param register: The register to return the value from
        :returns the value stored in the register
        """
        if not Vm.is_register(register):
            raise ValueError("Expected register value, instead got: " + str(register))
        return self.registers[(register - REGISTER_0)]

    def get_a_param(self):
        """ Grab and validate the a operation parameter from exec_pointer + 1
        :returns value from that point in memory.
        """
        value = self.memory[self.exec_ptr + 1]
        Vm.validate_value(value)
        return value

    def get_b_param(self):
        """ Grab and validate the a operation parameter from exec_pointer + 2
        :returns value from that point in memory.
        """
        value = self.memory[self.exec_ptr + 2]
        Vm.validate_value(value)
        return value

    def get_c_param(self):
        """ Grab and validate the a operation parameter from exec_pointer + 3
        :returns value from that point in memory.
        """
        value = self.memory[self.exec_ptr + 3]
        Vm.validate_value(value)
        return value

    def stack_push(self, value):
        """ Push value onto the stack
        :param value: The value to push onto the stack
        """
        self.stack = numpy.insert(self.stack, 0, value)

    def stack_pop(self):
        """ Pop a value from the stack
        :returns value popped off from the stack
        """
        value = self.stack[0]
        self.stack = numpy.delete(self.stack, 0, 0)

        return value

    def read_memory(self, address):
        """Read the value from the passed in address and return it
        :param int address: The address to read from
        """
        return self.memory[Vm.filter_mem_address(address)]

    def write_memory(self, address, value):
        """Write the value to the specified address in memory
        :param int address: The address to write to
        :param int value: The value to write
        """
        self.memory[Vm.filter_mem_address(address)] = value

    def read_stack(self, offset):
        """Read the value from the passed in address and return it
        :param int offset: The offset to read from
        """
        self.validate_stack_offset(offset)
        return self.stack[offset]

    def write_stack(self, offset, value):
        """Write the value to the specified address in memory
        :param int offset: The address to write to
        :param int value: The value to write
        """
        self.validate_stack_offset(offset)
        self.stack[offset] = value

    def validate_stack_offset(self, offset):
        stack_size = len(self.memory)
        if stack_size == 0:
            raise ValueError("Invalid stack offset, stack is empty")

        if 0 > offset > stack_size - 1:
            raise ValueError("Invalid stack offset, must be between 0...%s: %s", (str(len(self.memory)), str(offset)))

    @staticmethod
    def validate_value(value):
        """ Validates that the passed in value is less than MAX_INT if it's not it raises a ValueError
        :param int value: The value to check
        :raises ValueError when the value is greater than MAX_INT
        """
        if value > MAX_VALID_VALUE:
            raise ValueError("Invalid value, greater than MAX_VALID_VALUE: " + str(value))

    @staticmethod
    def is_register(value):
        """ Checks to see if the passed in value is is a register or not.
        :param int value: An uint16 value
        :returns boolean True if it is a register and False otherwise
        """
        if REGISTER_0 <= value <= REGISTER_7:
            return True
        return False

    @staticmethod
    def filter_mem_address(address):
        """ Filters the passed in address to be a valid space in memory
        :param int address: The memory address to reference between 0 ... MAX_MEMORY_ADDRESS - 1
        """
        if not TOROIDAL_MEMORY and (address < 0 or address > MAX_MEMORY_ADDRESS):
            raise ValueError("Invalid memory address in non-toroidal memory mode. " + str(address))

        return address % (MAX_MEMORY_ADDRESS + 1)