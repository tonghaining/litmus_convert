#!/usr/bin/env python3

import ptx_output
import vulkan_output


class Store:
    def __init__(self, iid, loc, value):
        self.iid = iid
        self.loc = loc
        self.value = value


class EqGoto:
    def __init__(self, iid, loc, return_value, instruction_id):
        self.iid = iid
        self.loc = loc
        self.return_value = return_value
        self.instruction_id = instruction_id


class ExchGoto:
    def __init__(self, iid, loc, integer, return_value, instruction_id):
        self.iid = iid
        self.loc = loc
        self.integer = integer
        self.return_value = return_value
        self.instruction_id = instruction_id


class Dat3mProgram:
    def __init__(self):
        self.threads = {}
        self.locations = set()
        self.current_thread = None
        self.current_thread_id = None

    def add_location(self, loc):
        self.locations.add(loc)
        return loc

    def add_thread(self, tid):
        if self.current_thread is not None:
            self.threads[self.current_thread_id] = self.current_thread
        self.current_thread_id = tid
        self.current_thread = []

    def add_store(self, iid, loc, value):
        self.current_thread.append(Store(iid, loc, value))

    def add_eq_goto(self, iid, loc, return_value, instruction_id):
        self.current_thread.append(EqGoto(iid, loc, return_value, instruction_id))

    def add_exch_goto(self, iid, loc, integer, return_value, instruction_id):
        self.current_thread.append(ExchGoto(iid, loc, integer, return_value, instruction_id))

    def to_program(self):
        return self

    def close(self):
        self.threads[self.current_thread_id] = self.current_thread
        for tid in self.threads:
            for instruction in self.threads[tid]:
                if type(instruction).__name__ == 'EqGoto' or type(instruction).__name__ == 'ExchGoto':
                    if instruction.instruction_id == "END":
                        instruction.instruction_id = len(self.threads[tid]) - 1
                    else:
                        instruction.instruction_id = int(instruction.instruction_id)
        self.current_thread = None
        self.current_thread_id = None
