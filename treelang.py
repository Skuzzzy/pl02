
import sys

# def string_to_segment(segment_string):
    # lines = [split.strip() for split in segment_string.split('\n')]
    # code_lines = [code for code in lines if code]
    # without_comments = [code for code in code_lines if code[0] != '#']
    # return without_comments

# def is_int(s):
    # try:
        # int(s)
        # return True
    # except ValueError:
        # return False

# def resolve_var_or_imm(var, local_vars):
    # if is_int(var):
        # return var
    # else:
        # offset = (local_vars.index(var) + 1) * 4
        # return "[ebp - {}]".format(offset)

# def parse_segment(segment):
    # segment_code = []
    # # Set up stack frame
    # segment_code.append("push ebp")
    # segment_code.append("mov ebp, esp")





class ProgramData(object):
    def __init__(self):
        self.functions = []

    def add_function(self, function):
        self.functions.append(function)

    def emit(self):
        program = []
        program.append('bits 32')
        program.append('extern printf')
        program.append('global main')
        program.append('\tSECTION .data')
        program.append('dfmt: db "%d", 10, 0')
        program.append('\tSECTION .text')

        for function in self.functions:
            program.extend(function.code)
            program.append('\n')
        print "\n".join(program)


class FunctionData(object):
    def __init__(self, code_segment):
        self.name = None
        self.params = None
        self.local_variables = None
        self.code = []

        self.__parse_code_segment(code_segment)

    def __parse_code_segment(self, code):
        self.code = []
        # Params are in order of declaration
        # These affect the location of things on the stack
        params = []
        # Order of local variables determines location on stack
        local_variables = []
        for linenum, line in enumerate(code):
            context = (line, linenum)
            splitline = line.split()
            first = splitline[0]
            if first == "PARAM":
                params.append((splitline[1], context))

            if first == "NEW":
                local_variables.append((splitline[1], context))

            if first == "FUNC":
                self.name = (splitline[1], context)

        self.params = [param[0] for param in params]
        self.local_variables = [localvar[0] for localvar in local_variables]

        self.code.append("; {}".format(self.name))
        self.code.append("{}:".format(self.name[0]))
        self.code.append("push ebp")
        self.code.append("mov ebp, esp")
        stack_space = len(local_variables) * 4
        self.code.append("sub esp, {}".format(stack_space))
        self.code.append("")
        if params:
            self.code.append("; Parameters")
            for each in params:
                self.code.append("; {} is {}".format(each, self.__resolve_local_or_imm(each[0])))
            self.code.append("")
        if local_variables:
            self.code.append("; Local Variables")
            for each in local_variables:
                self.code.append("; {} is {}".format(each, self.__resolve_local_or_imm(each[0])))
            self.code.append("")

        # Now parse for other stuff
        for linenum, line in enumerate(code):
            context = (line, linenum)
            splitline = line.split()
            first = splitline[0]
            if len(splitline) > 1:
                second = splitline[1]

            if first[0] == "!":
                # This line is a label
                mini_segment = []
                mini_segment.append("; {}".format(context))
                mini_segment.append(first[1:] + ":")
                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "SET":
                mini_segment = []
                dest = self.__resolve_local(second)
                if self.__is_local(splitline[2]):
                    fromm = self.__resolve_local(splitline[2])
                else:
                    fromm = splitline[2]

                mini_segment.append("; {}".format(context))
                mini_segment.append("mov edx, {}".format(fromm))
                mini_segment.append("mov {}, edx".format(dest))
                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "ADD":
                dest = self.__resolve_local(second) # This must resolve or else program explodes for good reason
                mini_segment = []
                fromm = self.__resolve_local_or_imm(splitline[2])
                mini_segment.append("; {}".format(context))
                mini_segment.append("mov edx, {}".format(fromm))
                mini_segment.append("add dword {}, edx".format(dest))
                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "SUB":
                dest = self.__resolve_local(second) # This must resolve or else program explodes for good reason
                mini_segment = []
                fromm = self.__resolve_local_or_imm(splitline[2])
                mini_segment.append("; {}".format(context))
                mini_segment.append("mov edx, {}".format(fromm))
                mini_segment.append("sub dword {}, edx".format(dest))
                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "PRINT": # TEMP LANGUAGE FEATURE FOR BOOTSTRAPPING
                toprint = self.__resolve_local_or_imm(second)
                mini_segment = []
                mini_segment.append("; {}".format(context))
                mini_segment.append("push dword {}".format(toprint))
                mini_segment.append("push dword dfmt")
                mini_segment.append("call printf")
                mini_segment.append("add esp, 4*2")
                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "JUMP":
                mini_segment = []
                mini_segment.append("; {}".format(context))
                mini_segment.append("jmp {}".format(second))
                mini_segment.append("")
                self.code.extend(mini_segment)


            elif first == "JNEQ" or first == "JEQ":
                mini_segment = []
                [localvar[0] for localvar in local_variables]
                arg1 = self.__resolve_local_or_imm(second)
                arg2 = self.__resolve_local_or_imm(splitline[2])
                jump_dest = splitline[3] # THIS MUST BE A LOCAL JUMP TODO CHECK THIS
                mini_segment.append("; {}".format(context))
                mini_segment.append("mov edx, {}".format(arg1))
                mini_segment.append("mov ecx, {}".format(arg2))
                mini_segment.append("cmp edx, ecx")
                if first == "JNEQ":
                    mini_segment.append("jne {}".format(jump_dest))
                else:
                    mini_segment.append("je {}".format(jump_dest))

                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "FUNCALL":
                mini_segment = []
                mini_segment.append("; {}".format(context))
                # Push arguments on stack
                if len(splitline) > 2:
                    for arg in splitline[2:len(splitline)-1]:
                        mini_segment.append("push dword {}".format(self.__resolve_local_or_imm(arg)))

                mini_segment.append("call {}".format(second))
                arg1 = self.__resolve_local(splitline[len(splitline)-1])
                mini_segment.append("mov {}, eax".format(arg1))
                mini_segment.append("add esp, 4*{}".format(len(splitline)-3))
                mini_segment.append("")
                self.code.extend(mini_segment)

            elif first == "RETURN":
                mini_segment = []
                arg1 = self.__resolve_local_or_imm(second)
                mini_segment.append("; {}".format(context))
                mini_segment.append("mov eax, {}".format(arg1))
                mini_segment.append("mov eax, {}".format(arg1))
                mini_segment.append("")
                self.code.extend(mini_segment)
            else:
                pass
                # mini_segment = []
                # mini_segment.append("; NOT RECOGNIZED {}".format(context))
                # mini_segment.append("")
                # self.code.extend(mini_segment)


        self.code.append("mov esp, ebp")
        self.code.append("pop ebp")
        self.code.append("ret")
        # print "\n".join(self.code)


    def __resolve_local_or_imm(self, token):
        if self.__is_local(token):
            return self.__resolve_local(token)
        else:
            return token



    def __is_local(self, name):
        return (name in self.params) or (name in self.local_variables)

    def __resolve_local(self, name):
        if name in self.params:
            index = self.params.index(name)
            ebp_offset = 8 + (4*index)
            # Params are above the ebp
            return "[ebp+{}]".format(ebp_offset)

        if name in self.local_variables:
            index = self.local_variables.index(name)
            ebp_offset = 4*(index+1)
            # Local variables are below
            return "[ebp-{}]".format(ebp_offset)



# class CodeAsmTuple(object):
    # def __init__(self, code, asm):
        # self.code = '; ' + code
        # self.asm = asm

    # def to_list(self):
        # return [self.code, self.asm]



def parse_code_lines(code_lines):
    current_line = 0
    functions = []

    while current_line < len(code_lines):
        if code_lines[current_line].split()[0] == "FUNC":
            startfunc = current_line
            endfunc = current_line
            while code_lines[endfunc] != "ENDFUNC":
                endfunc += 1
            functions.append(FunctionData(code_lines[startfunc:endfunc+1]))

            current_line = endfunc + 1

    prog = ProgramData()
    for func in functions:
        prog.add_function(func)
    prog.emit()




def get_code_lines(filename):
    with open(filename) as code:
        code = [line.rstrip('\n').strip() for line in code.readlines() if line.rstrip('\n').strip()]
        return code


parse_code_lines(get_code_lines("tree4.tree"))
# code = "\n".join([line.rstrip('\n') for line in sys.stdin.readlines()])
# segment = string_to_segment(code)
# parsed =  parse_segment(segment)

# print("\n".join(segment_is_main(parsed)))

