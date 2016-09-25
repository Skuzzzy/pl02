from parser import parse

program = """
VAR x, squ;

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
def interpret(program_text):
    program = parse(program_text)
    print("")
    program.eval({}, {}, {})


interpret(program)