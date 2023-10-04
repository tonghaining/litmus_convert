#!/usr/bin/env python3

import os
import lark
from dat3m_litmus import *


################################################################################
# Litmus test parser
################################################################################

class ParseException(Exception):
    def init(self, text, meta, message):
        text = text[meta.start_pos: meta.end_pos]
        text = " ".join([i.strip() for i in text.split("\n")])
        self.message = f"Line {meta.line}: '{text}': {message}"

    def str(self):
        return self.message


@lark.v_args(inline=True, meta=True)
class Transformer(lark.Transformer):
    def init(self, text):
        self.text = text
        self.instruction_count = 0

    def start(self, meta, threads):
        return LitmusTest(
            threads=threads.children,
        )

    def thread(self, meta, tid, instructions):
        return Thread(
            tid=tid,
            instructions=instructions.children,
        )

    def store(self, meta, iid, loc, value):
        return Store(
            iid=iid,
            loc=loc,
            value=value,
            line=meta.line,
        )

    def eq_goto(self, meta, iid, loc, return_value, goto_label):
        return EqGoto(
            iid=iid,
            loc=loc,
            return_value=return_value,
            goto_label=goto_label,
            line=meta.line,
        )

    def exch_goto(self, meta, iid, loc, value, return_value, goto_label):
        return ExchGoto(
            iid=iid,
            loc=loc,
            value=value,
            return_value=return_value,
            goto_label=goto_label,
            line=meta.line,
        )

    def loc(self, meta, num):
        return Location(int(num))

    def return_value(self, meta, n):
        return int(n)

    def goto_label(self, meta, label=None):
        if label is None:
            return "END"
        return str(label)

    def num(self, meta, n):
        return int(n)


def parse(contents):
    file_path = os.path.dirname(os.path.realpath(__file__))
    grammar_path = os.path.join(file_path, "grammar.lark")
    with open(grammar_path, "r") as f:
        grammar = f.read()

    _parser = lark.Lark(grammar, propagate_positions=True)
    return Transformer(contents).transform(_parser.parse(contents))
