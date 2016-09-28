from tokenize import Token, tokenize
from abstract_syntax_tree import Const, Literal, Var, Procedure, Program, Block, Statement, Condition, Expression, Term, Factor
import traceback
import sys

def syntax_error(tokens, index, err_msg=""):
    print(str(tokens[index-1]), err_msg)
    traceback.print_stack()
    sys.exit(-1)

def get_token(tokens, index):
    return (index+1, tokens[index])

def unget_token(tokens, index):
    return index-1

def parse_program(tokens, index):
    # print "program"
    index, block = parse_block(tokens, index)
    index, token = get_token(tokens, index)
    if not token.literal == ".":
        syntax_error(tokens, index, "Expected period")
    if index < len(tokens):
        syntax_error(tokens, index, "End of program reached before end of token stream")
    return (index, block)

def parse_block(tokens, index):
    # print "block"
    constants = []
    index, token = get_token(tokens, index)
    if token.literal == "const":
        index, token = get_token(tokens, index)
        if token.token_type != "IDENT":
            syntax_error(tokens, index)
        ident = token
        index, token = get_token(tokens, index)
        if token.literal != "=":
            syntax_error(tokens, index)
        index, token = get_token(tokens, index)
        if token.token_type != "INT_LITERAL":
            syntax_error(tokens, index)
        literal = token
        constants.append(Const(ident, literal))

        index, token = get_token(tokens, index)
        while token.literal == ",":
            index, token = get_token(tokens, index)
            ident = token
            index, token = get_token(tokens, index)
            if token.literal != "=":
                syntax_error(tokens, index)
            index, token = get_token(tokens, index)
            if not token.token_type == "INT_LITERAL":
                syntax_error(tokens, index, "Expected a integer literal here")
            literal = token

            index, token = get_token(tokens, index)
            constants.append(Const(ident, literal))
        index = unget_token(tokens, index)
        index, token = get_token(tokens, index)
        if not token.literal == ";":
            syntax_error(tokens, index)
    else:
        index = unget_token(tokens, index)

    variables = []
    index, token = get_token(tokens, index)
    if token.literal == "var":
        index, token = get_token(tokens, index)
        if not token.token_type == "IDENT":
            syntax_error(tokens, index)
        ident = token

        variables.append(Var(ident))

        index, token = get_token(tokens, index)
        while token.literal == ",":
            index, token = get_token(tokens, index)
            if not token.token_type == "IDENT":
                syntax_error(tokens, index, "Vars must be of IDENT")
            ident = token
            variables.append(Var(ident))

            index, token = get_token(tokens, index)
        index = unget_token(tokens, index)
        index, token = get_token(tokens, index)
        if not token.literal == ";":
            syntax_error(tokens, index)

    else:
        index = unget_token(tokens, index)

    procedures = []
    index, token = get_token(tokens, index)
    while token.literal == "procedure":
        index, token = get_token(tokens, index)
        if not token.token_type == "IDENT":
            syntax_error(tokens, index)
        ident = token
        index, token = get_token(tokens, index)
        if not token.literal == ";":
            syntax_error(tokens, index)

        index, block = parse_block(tokens, index)

        index, token = get_token(tokens, index)
        if not token.literal == ";":
            syntax_error(tokens, index)

        procedures.append(Procedure(ident, block))

        index, token = get_token(tokens, index)

    index = unget_token(tokens, index)

    index, statement = parse_statement(tokens, index)

    block = Block(constants, variables, procedures, statement)
    return (index, block)

"""statement = [ ident ":=" expression | "call" ident
              | "!" expression
              | "begin" statement {";" statement } "end"
              | "if" condition "then" statement
              | "while" condition "do" statement ]."""
def parse_statement(tokens, index):
    index, token = get_token(tokens, index)
    # print token, "statement"
    if token.token_type == "IDENT":
        ident = token
        index, token = get_token(tokens, index)
        if not token.literal == ":=":
            syntax_error(tokens, index, "Expected a :=")
        operator = token
        index, expression = parse_expression(tokens, index)
        statement = Statement(operator, [ident, expression])
    elif token.token_type == "RESERVED" and token.literal == "call":
        operator = token
        index, token = get_token(tokens, index)
        if not token.token_type == "IDENT":
            syntax_error(tokens, index, "Expected identifier")
        ident = token
        statement = Statement(operator, [ident])
    elif token.literal == "!":
        operator = token
        index, expression = parse_expression(tokens, index)
        statement = Statement(operator, [expression])
    elif token.literal == "begin":
        operator = token
        statements = []

        index, statement = parse_statement(tokens, index)

        statements.append(statement)

        index, token = get_token(tokens, index)
        while token.literal == ";":
            index, statement = parse_statement(tokens, index)
            statements.append(statement)
            index, token = get_token(tokens, index)
        index = unget_token(tokens, index)
        index, token = get_token(tokens, index)
        if not token.literal == "end":
            syntax_error(tokens, index)

        statement = Statement(operator, statements)
    elif token.literal == "if":
        operator = token
        index, condition = parse_condition(tokens, index)

        index, token = get_token(tokens, index)
        if not token.literal == "then":
            syntax_error(tokens, index)

        index, statement = parse_statement(tokens, index)
        statement = Statement(operator, [condition, statement])
    elif token.literal == "while":
        operator = token
        index, condition = parse_condition(tokens, index)

        index, token = get_token(tokens, index)
        if not token.literal == "do":
            syntax_error(tokens, index)

        index, statement = parse_statement(tokens, index)

        statement = Statement(operator, [condition, statement])

    else:
        syntax_error(tokens, index, "Cannot be the start of a statement")

    return (index, statement)

def parse_condition(tokens, index):
    index, token = get_token(tokens, index)
    # print token, "condition"
    if token.literal == "odd":
        operator = token
        index, expression = parse_expression(tokens, index)
        condition = Condition(token, expression, None)
    else:
        index = unget_token(tokens, index)
        index, expression_one = parse_expression(tokens, index)
        index, token = get_token(tokens, index)
        if not token.token_type == "CMP":
            syntax_error(tokens, index)
        cmp_token = token

        index, expression_two = parse_expression(tokens, index)

        condition = Condition(cmp_token, expression_one, expression_two)

    return (index, condition)

def parse_expression(tokens, index):
    index, token = get_token(tokens, index)
    # print token, "expression"

    operation = Token("DNE", "DNE", "ADD", "+")
    if token.token_type == "ADD" or token.token_type == "SUB":
        operation = token
    else:
        index = unget_token(tokens, index)

    index, term = parse_term(tokens, index)
    expr_node = Expression(operation, term, None) # Dancing around special bullshit language feature
    root = expr_node

    index, token = get_token(tokens, index)
    while token.token_type == "ADD" or token.token_type == "SUB":
        index, term = parse_term(tokens, index)
        root = Expression(operation, root, term)

        index, token = get_token(tokens, index)

    index = unget_token(tokens, index)

    return (index, root)


def parse_term(tokens, index):
    # print "term"

    index, factor = parse_factor(tokens, index)

    root = factor;
    index, token = get_token(tokens, index)
    while token.token_type == "MUL" or token.token_type == "DIV":
        operation = token
        index, factor = parse_factor(tokens, index)
        root = Term(operation, root, factor)

        index, token = get_token(tokens, index)

    index = unget_token(tokens, index)

    return (index, root)

def parse_factor(tokens, index):
    # print "factor"
    index, token = get_token(tokens, index)
    if token.token_type == "IDENT":
        factor = Var(token)
    elif token.token_type == "INT_LITERAL":
        factor = Literal(token)
    elif token.token_type == "L-PAREN":
        index, expression = parse_expression(tokens, index)
        index, token = get_token(tokens, index)
        if not token.token_type == "R-PAREN":
            syntax_error(tokens, index, "Expected a R-PAREN")
        factor = expression
    else:
        syntax_error(tokens, index, "Token cannot produce a factor")

    return (index, Factor(factor))

def parse(program):
    for linum, line in enumerate(program.splitlines()):
        print linum, line
    tokens = tokenize(program)
    tokens = [token for token in tokens if token.token_type != "WHITESPACE"]
    index = 0
    index, result = parse_program(tokens, index)
    return result


if __name__ == "__main__":
    program = """
    VAR x, squ;

    /*
        This is a comment
    */

    PROCEDURE square;
    BEGIN
       squ:= x * x
    END;

    BEGIN
       x := 1;
       WHILE x <= 10 DO
       BEGIN
          CALL square;
          ! squ;
          x := x + 1
       END
    END.
    """

    # Don't you dare preach PEP-8 to me
    import jsonpickle
    import json
    import pprint
    pp = pprint.PrettyPrinter()
    # End Don't you dare preach PEP-8 to me
    frozen = jsonpickle.encode(parse(program))
    thawed = json.loads(frozen)
    print(parse(program))
    pp.pprint(thawed)
