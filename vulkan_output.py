from pretty_printer import pretty_print


class VulkanOutput:
    def __init__(self, name, program):
        self.name = name
        self.program = program
        self.reg = 0
        self.regs = {}
        self.labels = {}
        self.output = ""

    def get_register(self, tid):
        reg = f"r{self.reg}"
        if tid not in self.regs:
            self.regs[tid] = []
        self.regs[tid].append(reg)
        self.reg += 1
        return reg

    def _header(self):
        return f"VULKAN {self.name}\n"

    def _locations(self):
        location_declaration = "{\n"
        for location in self.program.locations:
            location_declaration += f"{location}=0;\n"
        for tid in self.regs:
            for reg in self.regs[tid]:
                location_declaration += f"P{tid}:{reg}=0;\n"
        location_declaration += "}\n"
        return location_declaration

    def _assertion(self):
        return "exists true"

    def expend_instruction(self, tid, instruction):
        if tid not in self.labels:
            self.labels[tid] = None
        current_label = self.labels[tid]
        res = []

        if type(instruction).__name__ == 'Store':
            res.append(f"st.atom.wg.sc0 {instruction.loc}, {instruction.value}")
        elif type(instruction).__name__ == 'EqGoto':
            if current_label != instruction.iid:
                res.append(f"LC{tid}{instruction.iid}:")
            reg = self.get_register(tid)
            res.append(f"ld.atom.wg.sc0.semsc0 {reg}, {instruction.loc}")  # .acq?
            res.append(f"beq {reg}, {instruction.return_value}, LC{tid}{instruction.instruction_id + 1}")
            res.append(f"goto LC{tid}{instruction.iid}")
            res.append(f"LC{tid}{instruction.iid + 1}:")
            self.labels[tid] = instruction.iid + 1
        elif type(instruction).__name__ == 'ExchGoto':
            if current_label != instruction.iid:
                res.append(f"LC{tid}{instruction.iid}:")
            reg = self.get_register(tid)
            res.append(f"rmw.atom.wg.sc0.semsc0 {reg}, {instruction.loc}, {instruction.integer}")  # .acq?
            res.append(f"beq {reg}, {instruction.return_value}, LC{tid}{instruction.instruction_id + 1}")
            res.append(f"goto LC{tid}{instruction.iid}")
            res.append(f"LC{tid}{instruction.iid + 1}:")
            self.labels[tid] = instruction.iid + 1
        return res

    def expend_threads(self):
        thread_map = {}
        for tid in self.program.threads:
            res = []
            for instruction in self.program.threads[tid]:
                res.extend(self.expend_instruction(tid, instruction))
            thread_map[f"P{tid}@sg 0,wg 0, qf 0"] = res
        return thread_map

    def dat3m_print(self):
        self.output += self._header()
        thread_map = self.expend_threads()
        self.output += self._locations()
        pretty_thread = pretty_print(thread_map)
        self.output += pretty_thread
        self.output += self._assertion()
        return self.output
