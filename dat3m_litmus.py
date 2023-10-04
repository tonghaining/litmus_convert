from dat3m_program import *


################################################################################
# Exception class with line number information
################################################################################


class LitmusException(Exception):
    def __init__(self, line, msg):
        self.line = line
        self.msg = msg

    def __str__(self):
        return f"Line {self.line}: {self.msg}"


################################################################################
# Litmus test abstract syntax tree
################################################################################


class Location:
    def __init__(self, name, line=None):
        self.name = name
        self.line = line

    def __str__(self):
        return self.name

    def to_program(self, test_program):
        return test_program.add_location(f"Mem{self.name}")


class Thread:
    def __init__(self, tid, instructions):
        self.tid = tid
        self.instructions = instructions

    def __str__(self):
        return f"Thread {self.tid}: {self.instructions}"

    def to_program(self, test_program):
        test_program.add_thread(self.tid)
        for instruction_tree in self.instructions:
            for instruction in instruction_tree.children:
                instruction.to_program(test_program)


################################################################################
# Instructions
################################################################################


class Instruction:
    pass


class Store(Instruction):
    def __init__(self, iid, loc, value, line=None):
        self.iid = iid
        self.loc = loc
        self.value = value
        self.line = line

    def __str__(self):
        return f"Store {self.loc} <- {self.value}"

    def to_program(self, test_program):
        test_program.add_store(self.iid, self.loc.to_program(test_program), self.value)


class EqGoto(Instruction):
    def __init__(self, iid, loc, return_value, goto_label, line=None):
        self.iid = iid
        self.loc = loc
        self.return_value = return_value
        self.goto_label = goto_label
        self.line = line

    def __str__(self):
        return f"EqGoto {self.loc} == {self.return_value} -> {self.goto_label}"

    def to_program(self, test_program):
        test_program.add_eq_goto(self.iid, self.loc.to_program(test_program), self.return_value, self.goto_label)


class ExchGoto(Instruction):
    def __init__(self, iid, loc, value, return_value, goto_label, line=None):
        self.iid = iid
        self.loc = loc
        self.value = value
        self.return_value = return_value
        self.goto_label = goto_label
        self.line = line

    def __str__(self):
        return f"ExchGoto {self.loc} == {self.value} -> {self.return_value} -> {self.goto_label}"

    def to_program(self, test_program):
        test_program.add_exch_goto(self.iid, self.loc.to_program(test_program), self.value, self.return_value,
                                   self.goto_label)


################################################################################
# Litmus program
################################################################################


class LitmusTest:
    def __init__(self, threads):
        self.dat3mProgram = Dat3mProgram()
        self.threads = threads

    def __str__(self):
        return f"LitmusTest {self.name}: {self.locations}, {self.threads}"

    def to_program(self):
        for t in self.threads:
            t.to_program(self.dat3mProgram)
        self.dat3mProgram.close()
        return self.dat3mProgram
