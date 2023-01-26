from typing import Set

from antlr4 import ParserRuleContext
from pyformlang.finite_automaton import EpsilonNFA

from project.finite_automata import build_nfa_from_graph
from project.gql.ASLParser import ASLParser
from project.gql.ASLVisitor import ASLVisitor
from project.graph_module import get_graph_by_name
from project.interpreter.exceptions import InterpreterException
from project.rpq import rpq_interpreter


class InterpreterVisitor(ASLVisitor):
    def __init__(self):
        self.local_stacks = [{}]
        self.output = ""

    def add_local_stack(self, local_stacks: dict):
        self.local_stacks.append(local_stacks)

    def pop_local_stack(self):
        if len(self.local_stacks) <= 1:
            raise InterpreterException("Attempt to pop global scope")
        self.local_stacks.pop()

    def set_variable(self, variable: str, value):
        self.local_stacks[-1][variable] = value

    def find_variable(self, var: str):
        for local_stack in reversed(self.local_stacks):
            if var in local_stack:
                return local_stack[var]
        raise InterpreterException(f"Unknown variable: {var}")

    def visitStat(self, ctx: ASLParser.StatContext):
        if ctx.var():
            var = self.get_string(ctx.var())
            value = self.visitExpr(ctx.expr())
            self.set_variable(var, value)
        else:
            value = self.visitExpr(ctx.expr())
            if self.output:
                self.output += "\n"
            self.output += str(value)

    @staticmethod
    def get_string(ctx: ParserRuleContext):
        string = ""
        for token in ctx.getChildren():
            string += str(token)
        return string

    def visitVar(self, ctx: ASLParser.VarContext):
        return self.find_variable(self.get_string(ctx))

    def visitVal(self, ctx: ASLParser.ValContext):
        if ctx.string():
            return self.visit(ctx.string())
        if ctx.char():
            return self.visit(ctx.char())
        if ctx.int_():
            return self.visit(ctx.int_())
        if ctx.boolean():
            return self.visit(ctx.boolean())
        if ctx.set_():
            return self.visit(ctx.set_())
        if ctx.graph():
            return self.visit(ctx.graph())
        if ctx.vertices():
            return self.visit(ctx.vertices())
        if ctx.edges():
            return self.visit(ctx.edges())
        if ctx.labels():
            return self.visit(ctx.labels())

    def visitString(self, ctx: ASLParser.StringContext):
        return self.get_string(ctx)

    def visitChar(self, ctx: ASLParser.CharContext):
        return self.get_string(ctx)

    def visitInt(self, ctx: ASLParser.IntContext):
        return int(self.get_string(ctx))

    def visitBoolean(self, ctx: ASLParser.BooleanContext):
        return str(ctx.getChild(0)) == "true"

    def visitSet(self, ctx: ASLParser.SetContext):
        return set(self.visit(child) for child in ctx.val())

    def visitGraph(self, ctx: ASLParser.GraphContext):
        if ctx.var():
            graph = self.visit(ctx.var())
            if not isinstance(graph, EpsilonNFA):
                raise InterpreterException(f"Expected graph, but found: {type(graph)}")
            return graph
        if ctx.getChild(0).getText() == "load_graph":
            name = self.visit(ctx.string())
            return build_nfa_from_graph(get_graph_by_name(name), [], [])
        vertices = self.visit(ctx.vertices())
        graph: EpsilonNFA = self.visit(ctx.graph())

        if ctx.getChild(0).getText() == "add_start":
            for state in vertices:
                graph.add_start_state(state)
            return graph
        if ctx.getChild(0).getText() == "add_final":
            for state in vertices:
                graph.add_final_state(state)
            return graph

        graph_new = graph.copy()
        if ctx.getChild(0).getText() == "set_start":
            for state in graph.start_states:
                graph_new.remove_start_state(state)
            for state in vertices:
                graph_new.add_start_state(state)
            return graph_new
        if ctx.getChild(0).getText() == "set_final":
            for state in graph.final_states:
                graph_new.remove_final_state(state)
            for state in vertices:
                graph_new.add_final_state(state)
            return graph_new

    def visitPath(self, ctx: ASLParser.PathContext):
        return self.get_string(ctx)

    def visitVertices(self, ctx: ASLParser.VerticesContext):
        if ctx.var():
            vertices = self.visit(ctx.var())
            if not isinstance(vertices, Set):
                raise InterpreterException(
                    f"Expected set of vertices, but found: {type(vertices)}"
                )
            return vertices
        if ctx.set_():
            vertices = self.visit(ctx.set_())
            if not isinstance(vertices, Set):
                raise InterpreterException(
                    f"Expected set of vertices, but found: {type(vertices)}"
                )
            return vertices

        graph: EpsilonNFA = self.visit(ctx.graph())
        command = ctx.getChild(0).getText()
        if command == "get_start":
            return graph.start_states
        if command == "get_final":
            return graph.final_states
        if command == "get_vertices":
            return graph.states
        if command == "get_reachable":
            return rpq_interpreter(graph)
        self.visitChildren(ctx)

    def visitEdges(self, ctx: ASLParser.EdgesContext):
        if ctx.var():
            edges = self.visit(ctx.var())
            if not isinstance(edges, Set):
                raise InterpreterException(
                    f"Expected set of edges, but found: {type(edges)}"
                )
            return edges
        if ctx.set_():
            edges = self.visit(ctx.set_())
            if not isinstance(edges, Set):
                raise InterpreterException(
                    f"Expected set of edges, but found: {type(edges)}"
                )
            return edges
        if ctx.getChild(0).getText() == "get_edges":
            graph: EpsilonNFA = self.visit(ctx.graph())
            return set(graph.transition_function)

    def visitLabels(self, ctx: ASLParser.LabelsContext):
        if ctx.var():
            labels = self.visit(ctx.var())
            if not isinstance(labels, Set):
                raise InterpreterException(
                    f"Expected set of labels, but found: {type(labels)}"
                )
            return labels
        if ctx.set_():
            labels = self.visit(ctx.set_())
            if not isinstance(labels, Set):
                raise InterpreterException(
                    f"Expected set of labels, but found: {type(labels)}"
                )
            return labels
        if ctx.getChild(0).getText() == "get_labels":
            graph: EpsilonNFA = self.visit(ctx.graph())
            return graph.symbols
