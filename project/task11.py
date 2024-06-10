from project.lang.langLexer import langLexer
from project.lang.langVisitor import langVisitor
from project.lang.langParser import langParser
from antlr4 import *
from antlr4.InputStream import InputStream


class CntVisitor(langVisitor):
    def __init__(self):
        super(langVisitor, self).__init__()
        self.cnt = 0

    def enter_rule(self, rule):
        self.cnt += 1


class SerializeVisitor(langVisitor):
    def __init__(self):
        super(langVisitor, self).__init__()
        self.res = ""

    def enter_rule(self, rule):
        self.res += rule.getText()


def prog_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    entry = CommonTokenStream(langLexer(InputStream(program)))
    parser = langParser(entry)
    prog = parser.prog()
    correct = parser.getNumberOfSyntaxErrors() == 0
    return (prog, correct)


def nodes_count(tree: ParserRuleContext) -> int:
    vis = CntVisitor()
    tree.accept(vis)
    return vis.cnt


def tree_to_prog(tree: ParserRuleContext) -> str:
    vis = SerializeVisitor()
    tree.accept(vis)
    return vis.res
