from tokenize import Token
import sys

def ast_error(ast_node, const_context, var_context, proc_context, message=""):
    print(ast_node, const_context, var_context, proc_context, message)
    sys.exit(-1)


class Const(object):
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value

    def eval(self, const_context, var_context, proc_context):
        # print(self.value)
        return int(self.value.literal)

    # def validate(self, const_context, var_context, proc_context):
        # try:
            # int(self.value.literal)
        # except ValueError as e:
            # ast_error(self, const_context, var_context, proc_context, "Invalid const literal \"{}\"".format(self.value.literal))

class Literal(object):
    def __init__(self, value):
        self.value = value

    def eval(self, const_context, var_context, proc_context):
        return int(self.value.literal)

class Var(object):
    def __init__(self, ident):
        self.ident = ident

    def eval(self, const_context, var_context, proc_context):
        if self.ident.literal in var_context:
            return var_context[self.ident.literal]
        if self.ident.literal in const_context:
            return const_context[self.ident.literal]
        1/0

class Procedure(object):
    def __init__(self, ident, block):
        self.ident = ident
        self.block = block

class Program(object):
    def __init__(self, block):
        self.block = block

class Block(object):
    def __init__(self, constants, variables, procedures, statement):
        self.constants = constants
        self.variables = variables
        self.procedures = procedures
        self.statement = statement

    def eval(self, const_context, var_context, proc_context):
        for const_decl in self.constants:
            const_context[const_decl.ident] = const_decl.eval(const_context, var_context, proc_context)
        for var_decl in self.variables:
            var_context[var_decl.ident.literal] = None
        for proc_decl in self.procedures:
            proc_context[proc_decl.ident.literal] = proc_decl.block
        statement = self.statement
        return statement.eval(const_context, var_context, proc_context)

class Statement(object):
    def __init__(self, operator, argument_list):
        self.operator = operator # call, begin, !, :=
        self.argument_list = argument_list

    def eval(self, const_context, var_context, proc_context):
        if self.operator.literal == "call":
            proc_context[self.argument_list[0].literal].eval(const_context, var_context, proc_context)
        elif self.operator.literal == "begin":
            for statement in self.argument_list:
                statement.eval(const_context, var_context, proc_context)
        elif self.operator.literal == "!":
            print(self.argument_list[0].eval(const_context, var_context, proc_context))
        elif self.operator.literal == ":=":
            if self.argument_list[0].literal in var_context:
                var_context[self.argument_list[0].literal] = self.argument_list[1].eval(const_context, var_context, proc_context)
            else:
                ast_error(self, const_context, var_context, proc_context, "Attempted assignment to name {} that does not exist as a variable".format(self.argument_list[0].literal))
        elif self.operator.literal == "while":
            while self.argument_list[0].eval(const_context, var_context, proc_context):
                self.argument_list[1].eval(const_context, var_context, proc_context)
        elif self.operator.literal == "if":
            if self.argument_list[0].eval(const_context, var_context, proc_context):
                self.argument_list[1].eval(const_context, var_context, proc_context)
        else:
            print(self.operator.literal)
            1/0 # TODO FIXME

class Condition(object):
    def __init__(self, operator, expr1, expr2=None):
        self.operator = operator
        self.expr1 = expr1
        self.expr2 = expr2

    def eval(self, const_context, var_context, proc_context):
        if self.operator.literal == "=":
            return 1 if self.expr1.eval(const_context, var_context, proc_context) == self.expr2.eval(const_context, var_context, proc_context) else 0
        elif self.operator.literal == "<":
            return 1 if self.expr1.eval(const_context, var_context, proc_context) < self.expr2.eval(const_context, var_context, proc_context) else 0
        elif self.operator.literal == ">":
            return 1 if self.expr1.eval(const_context, var_context, proc_context) > self.expr2.eval(const_context, var_context, proc_context) else 0
        elif self.operator.literal == ">=":
            return 1 if self.expr1.eval(const_context, var_context, proc_context) >= self.expr2.eval(const_context, var_context, proc_context) else 0
        elif self.operator.literal == "<=":
            return 1 if self.expr1.eval(const_context, var_context, proc_context) <= self.expr2.eval(const_context, var_context, proc_context) else 0
        # elif self.operator.literal == "#": # TODO TODO VERIFY THIS FIXME No idea what thhis operator does, not listed in spec
            # return 1 if (self.expr1.eval(const_context, var_context, proc_context) % self.expr2.eval(const_context, var_context, proc_context)) == 0 else 0
        elif self.operator.literal == "odd":
            return 1 if (self.expr1.eval(const_context, var_context, proc_context) % 2 != 0) else 0
        else:
            1/0 # TODO FIXME

class Expression(object):
    def __init__(self, operator, term1, term2):
        self.operator = operator
        self.term1 = term1
        self.term2 = term2 if term2 else Literal(Token("DNE", "DNE", "INT_LITERAL", "0"))

    def eval(self, const_context, var_context, proc_context):
        if self.operator.literal == "+":
            return self.term1.eval(const_context, var_context, proc_context) + self.term2.eval(const_context, var_context, proc_context)
        elif self.operator.literal == "-":
            return self.term1.eval(const_context, var_context, proc_context) - self.term2.eval(const_context, var_context, proc_context)
        else:
            1/0 # TODO FIXME

class Term(object):
    def __init__(self, operator, factor1, factor2):
        self.operator = operator
        self.factor1 = factor1
        self.factor2 = factor2 if factor2 else Literal(Token("DNE", "DNE", "INT_LITERAL", "1"))

    def eval(self, const_context, var_context, proc_context):
        if self.operator.literal == "/":
            return self.factor1.eval(const_context, var_context, proc_context) / self.factor2.eval(const_context, var_context, proc_context)
        elif self.operator.literal == "*":
            return self.factor1.eval(const_context, var_context, proc_context) * self.factor2.eval(const_context, var_context, proc_context)
        else:
            1/0 # TODO FIXME

class Factor(object):
    def __init__(self, value):
        self.value = value

    def eval(self, const_context, var_context, proc_context):
        return self.value.eval(const_context, var_context, proc_context)
