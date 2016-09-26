import sys


class Token(object):
    def __init__(self, linenum, column, token_type, literal):
        self.linenum = linenum
        self.column = column
        self.token_type = token_type
        self.literal = literal

    def __repr__(self):
        return "(Linenum:{}, Column:{}, TokenType:{}, Literal:{})".format(self.linenum, self.column, self.token_type, self.literal)

def syntax_error(text, index, linenum, col):
    print("SYNTAX ERROR: At index:{0}, linenum:{1}, column:{2}".format(index, linenum, col))
    print(" "*(col) + "|")
    print(" "*(col) + "V")
    print(text.splitlines()[linenum])
    sys.exit(-1)


reserved_words = {"const", "var", "procedure", "call", "begin", "end", "if", "then", "while", "do", "odd"}

def tokenize(text):
    tokens = []
    index = 0

    linenum = 0
    col = 0

    while index < len(text):
        if text[index].isspace():
            start_linenum = linenum
            start_col = col
            while (index < len(text)) and text[index].isspace():
                if text[index] == '\n':
                    linenum += 1
                    index += 1
                    col = 0
                else:
                    col += 1
                    index += 1
            # We are now at a nonspace
            # TODO Do I want to make the literal reflect the actual whitespace?
            tokens.append(Token(start_linenum, start_col, "WHITESPACE", " "))
        elif text[index] == "/":
            index += 1
            col += 1
            if text[index] != "*":
                tokens.append(Token(linenum, col, "DIV", "/"))
            while (index < len(text)):
                if text[index] == "*":
                    if(index+1 < len(text)):
                        index += 1
                        col += 1
                        if text[index] == "/":
                            index += 1
                            col += 1
                            break
                    else:
                        syntax_error(text, index, linenum, col)
                if text[index] == '\n':
                    linenum += 1
                    index += 1
                    col = 0
                else:
                    col += 1
                    index += 1

        elif text[index] == ".":
            tokens.append(Token(linenum, col, "PERIOD", "."))
            index += 1
            col += 1

        elif text[index] == "!":
            tokens.append(Token(linenum, col, "PRINT", "!"))
            index += 1
            col += 1

        elif text[index] == "*":
            tokens.append(Token(linenum, col, "MUL", "*"))
            index += 1
            col += 1

        elif text[index] == "+":
            tokens.append(Token(linenum, col, "ADD", "+"))
            index += 1
            col += 1

        elif text[index] == "-":
            tokens.append(Token(linenum, col, "SUB", "-"))
            index += 1
            col += 1

        elif text[index] == "(":
            tokens.append(Token(linenum, col, "L-PAREN", "("))
            index += 1
            col += 1

        elif text[index] == ")":
            tokens.append(Token(linenum, col, "R-PAREN", ")"))
            index += 1
            col += 1

        elif text[index] == ";":
            tokens.append(Token(linenum, col, "SEMICOLON", ";"))
            index += 1
            col += 1

        elif text[index] == ",":
            tokens.append(Token(linenum, col, "COMMA", ","))
            index += 1
            col += 1

        elif text[index] == ",":
            tokens.append(Token(linenum, col, "COMMA", ","))
            index += 1
            col += 1

        elif text[index] == ":":
            start_col = col
            index += 1
            col += 1
            if not text[index] == "=":
                syntax_error(text, index, linenum, col)
            else:
                tokens.append(Token(linenum, start_col, "SET", ":="))
                index += 1
                col += 1

        elif text[index] in {"=", "#", "<", ">"}:
            cmp_op = text[index]
            start_col = col
            index += 1
            col += 1
            if cmp_op in {"<", ">"} and text[index] == "=":
                cmp_op += text[index]
                index += 1
                col += 1
            tokens.append(Token(linenum, start_col, "CMP", cmp_op))

        elif text[index].isalpha():
            word_parts = [text[index]]
            start_col = col
            index += 1
            col += 1
            while text[index].isalnum():
                word_parts.append(text[index])
                index += 1
                col += 1
            token_string = "".join(word_parts)
            if token_string.lower() in reserved_words:
                tokens.append(Token(linenum, start_col, "RESERVED", token_string.lower()))
            else:
                tokens.append(Token(linenum, start_col, "IDENT", token_string))
        elif text[index].isdigit():
            integer_buf = [text[index]]
            start_col = col
            index += 1
            col += 1
            while text[index].isdigit():
                integer_buf.append(text[index])
                index += 1
                col += 1
            int_string = "".join(integer_buf)
            tokens.append(Token(linenum, start_col, "INT_LITERAL", int_string))
        else:
            syntax_error(text, index, linenum, col)

    return tokens

# print(tokenize(program))
