from pretty_printer import pretty_print


class VulkanOutput:
    def __init__(self, name, program, link):
        self.name = name
        self.program = program
        self.link = link
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

    def _comments(self):
        return f"\"https://github.com/tyler-utah/AlloyForwardProgress/blob/master/artifact/cadp/{self.link[0]}/alloy_output/{self.link[1]}/{self.name}.txt\"\n"

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
        return "exists 0==0"

    def expend_instruction(self, tid, instruction):

        if tid not in self.labels:
            self.labels[tid] = None

        current_label = self.labels[tid]
        res = []

        if current_label != instruction.iid:
            res.append(f"LC{tid}{instruction.iid}:")

        if type(instruction).__name__ == 'Store':
            res.append(f"st.atom.wg.sc0 {instruction.loc}, {instruction.value}")
        elif type(instruction).__name__ == 'EqGoto':
            reg = self.get_register(tid)
            res.append(f"ld.atom.wg.sc0.semsc0 {reg}, {instruction.loc}")  # .acq?
            res.append(f"beq {reg}, {instruction.return_value}, LC{tid}{instruction.iid + 1}")
            res.append(f"goto LC{tid}{instruction.target_label}")
        elif type(instruction).__name__ == 'ExchGoto':
            reg = self.get_register(tid)
            res.append(f"rmw.atom.wg.sc0.semsc0 {reg}, {instruction.loc}, {instruction.value}")  # .acq?
            res.append(f"beq {reg}, {instruction.return_value}, LC{tid}{instruction.iid + 1}")
            res.append(f"goto LC{tid}{instruction.target_label}")

        res.append(f"LC{tid}{instruction.iid + 1}:")
        self.labels[tid] = instruction.iid + 1

        return res

    def expend_threads(self):
        thread_map = {}
        for tid in self.program.threads:
            res = []
            for instruction in self.program.threads[tid]:
                res.extend(self.expend_instruction(tid, instruction))
                # Add label to the end of the thread
                if "LC" not in res[-1]:
                    res.append(f"LC{tid}{len(self.program.threads[tid])}:")
            thread_map[f"P{tid}@sg 0,wg 0, qf 0"] = res
        return thread_map

    def dat3m_print(self):
        self.output += self._header()
        self.output += self._comments()
        thread_map = self.expend_threads()
        self.output += self._locations()
        pretty_thread = pretty_print(thread_map)
        self.output += pretty_thread
        self.output += self._assertion()
        return self.output
