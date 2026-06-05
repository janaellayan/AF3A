KEYWORDS = {
    "sahih", # int
    "kasr",# double or float

    "kalema",# string

    "manteq",# bool

    "etha",# if(){}
    "aw",# else{}
    "talama", #while(expression){}

    "itba3",#print() 
    "da5el",#cin            input val;

    "shoghol",# function    function name_function() {}
    "lkol",# for            for(declaration/assignment; expression; math_statment ) {}
    "waqef",# break         stop;
    "kammel",# continue    continue;
    "raje3",# return       return val;

    "sa7",#true 
    "ghalat"#fale
}


TOKEN_TYPES = {
    "KEYWORD",
    "IDENTIFIER",
    "INTEGER",
    "FLOAT",
    "STRING",
    "OPERATOR",
    "SEMICOLON",
    "COMMA",
    "LPAREN",   # (
    "RPAREN",   # )
    "LBRACE",   # {
    "RBRACE"    # }
}

#===============================================================================================================
import re

class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.token_type}('{self.value}') at line {self.line}, column {self.column}"

#=======================================================================
class CompilerError:
    def __init__(self, error_type, message, line, column):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.column = column

    def __repr__(self):
        return f"[{self.error_type}] line {self.line}, column {self.column}: {self.message}"

#===============================================================================================================
def lexer(code):#breaks down the statement
    tokens = []
    errors = []

    token_patterns = [
        ("FLOAT", r"\d+\.\d+"),
        ("INTEGER", r"\d+"),
        ("STRING", r'"[^"]*"'),
        ("OPERATOR", r"==|!=|<=|>=|&&|\|\||[+\-*/%=<>!]"),
        ("SEMICOLON", r";"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("COMMA", r","),
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t]+"),
        ("MISMATCH", r".")
    ]

    combined_regex = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in token_patterns
    )

    line = 1
    line_start = 0

    for match in re.finditer(combined_regex, code):
        token_type = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if token_type == "NEWLINE":
            line += 1
            line_start = match.end()

        elif token_type == "SKIP":
            continue

        elif token_type == "MISMATCH":
            errors.append(
                    CompilerError(
                    "Lexical Error",
                    f"Invalid character '{value}'",
                    line,
                    column
                    )
            )

        else:
            if token_type == "IDENTIFIER"and value in KEYWORDS:
                token_type = "KEYWORD"

            tokens.append(Token(token_type, value, line, column))

    tokens.append(Token("EOF", "EOF", line, 1))

    return tokens, errors

#===============================================================================================================
# Abstract Syntax Tree node classes
class ASTNode:
    pass



class VarDeclaration(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"VarDeclaration(name={self.name}, value={self.value})"


class InputStatement(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"InputStatement(name = {self.name})"
    
class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.body = body
        self.condition = condition
    def __repr__(self):
        return f"WhileStatement(condition={self.condition}, body={self.body})"

class IfStatement(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body # 'aw' or 'aw etha'
    
    def __repr__(self):
        if self.else_body:
            return f"IfStatement(condition={self.condition}, body={self.body}, else_body={self.else_body})"
        return f"IfStatement(condition={self.condition}, body={self.body})"



class PrintStatement(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"PrintStatement(value={self.value})"


class BlockStatement(ASTNode):
        def __init__(self, statements):
            self.statements = statements

        def __repr__(self):
            return f"BlockStatement(\n  " + "\n  ".join(repr(s) for s in self.statements) + "\n)"    

class ContinueStatement(ASTNode):
    def __repr__(self):
        return "ContinueStatement"
    
class ReturnStatement(ASTNode):
    def __repr__(self):
        return "ReturnSatement"
class BreakStatement(ASTNode):
    def __repr__(self):
        return "BreakStatement"
    
class Expressions(ASTNode):
    def __init__(self, arg1, exp, arg2):
        self.arg1 = arg1
        self.exp = exp
        self.arg2 = arg2
    
    def __repr__(self):
        return f"Expression(left={self.arg1}, op='{self.exp}', right={self.arg2})"
    

class AssignmentStatement(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"AssignmentStatement(name={self.name}, value={self.value})"
    
class FunctionDeclaration(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self):
        return f"FunctionDeclaration(name={self.name}, body={self.body})"

class ForStatement(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __repr__(self):
        return f"ForStatement(\n  init={self.init},\n  cond={self.condition},\n  update={self.update},\n  body={self.body}\n)"

#===============================================================================================================



class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.ast = []

    def peek(self):
        return self.tokens[self.current]

    def advance(self):
        self.current += 1

    def match(self, expected):
        token = self.peek()

        if token.token_type == expected:
            self.advance()
            return True

        self.errors.append(
                    CompilerError(
                    "Syntax Error",
                    f"Expected {expected} but found {token.token_type} '{token.value}'",
                    token.line,
                    token.column
                    )
        )
        return False

    def syntax_error(self, message):
        token = self.peek()

        self.errors.append(
            CompilerError(
                "Syntax Error",
                message,
                token.line,
                token.column
            )
    )

    def synchronize(self):
        while self.peek().token_type != "EOF":
            if self.peek().token_type == "SEMICOLON":
                self.advance()
                return

            if self.peek().token_type == "RBRACE":
                return

            self.advance()
            

    def parse_declaration(self):

        
        self.match("KEYWORD")

        
        if self.peek().token_type != "IDENTIFIER":
            self.errors.append("Expected variable name")
            return

        name = self.peek().value
        self.advance()

        
        if self.peek().token_type == "OPERATOR" and self.peek().value == "=":
            self.advance()
        else:
            self.errors.append("Missing '='")
            return

        
        value = self.parse_expression()
        if value is None:
            return

        
        if self.peek().token_type == "SEMICOLON":
            self.advance()
        else:
            self.errors.append("Missing semicolon")
            return

        
        return VarDeclaration(name, value)








    def parse_print(self):#this is new
        
        self.match("KEYWORD") #checks expexted

        if self.peek().token_type != "LPAREN":
            self.errors.append("Expected (")
            return
        else:
            self.advance()
        
    

        if self.peek().token_type == "STRING" or self.peek().token_type == "INTEGER" or self.peek().token_type == "FLOAT" or self.peek().token_type == "IDENTIFIER":
            value = self.peek().value
            self.advance()
        else:
            self.errors.append('Expected argument types: STRING or INTEGER or FLOAT')
            return
        
        

        if self.peek().token_type != "RPAREN":
            self.errors.append("Expected )")
            return
        else:
            self.advance()
        
        
        if self.peek().token_type != "SEMICOLON":
            self.errors.append("Expected ;")
            return
        else:
            self.advance()
        
        
        return PrintStatement(value)



    def parse_input(self):
        self.match("KEYWORD")

        # da5el var_name;
        if self.peek().token_type == "IDENTIFIER":
            name = self.peek().value
            self.advance()
        else:
            return
        
        self.match("SEMICOLON")

        return InputStatement(name)
        




    def parse_return(self):
        self.match("KEYWORD")
        if not self.match("SEMICOLON"):
            return None
        return ReturnStatement()

    def parse_break(self):
        self.match("KEYWORD")
        if not self.match("SEMICOLON"):
            return None
        return BreakStatement()


    def parse_continue(self):
        self.match("KEYWORD")
        if not self.match("SEMICOLON"):
            return None
        return ContinueStatement()

    def parse_function(self):
        self.match("KEYWORD") # matches 'shoghol'
        
        if self.peek().token_type != "IDENTIFIER":
            self.errors.append("Expected function name")
            return None
            
        name = self.peek().value
        self.advance()

        
        if not self.match("LPAREN"): return None
        if not self.match("RPAREN"): return None

        # Parse the block {}
        body = self.parse_statement() 
        
        return FunctionDeclaration(name, body)

    def parse_while(self):
        self.match("KEYWORD") # matches 'talama'

        
        if self.peek().token_type != "LPAREN":
            self.errors.append("Expected '('")
            return 
        else:
            self.advance()
        
        condition = self.parse_expression()
        if condition == None:
            return None
        
            


        
        if self.peek().token_type != "RPAREN":
            self.errors.append("Expected ')'")
            return
        else:
            self.advance()

        
        body = self.parse_statement()

        
        return WhileStatement(condition, body)

    def parse_assignment(self, require_semicolon=True):
        name = self.peek().value
        self.advance() # Consume IDENTIFIER

        if self.peek().token_type == "OPERATOR" and self.peek().value == "=":
            self.advance()
        else:
            self.errors.append("Expected '=' in assignment")
            return None

        value = self.parse_expression()
        if value is None:
            return None


        if require_semicolon:
            if self.peek().token_type == "SEMICOLON":
                self.advance()
            else:
                self.errors.append("Expected ';' after assignment")
                return None

        return AssignmentStatement(name, value)


    def parse_block(self):
        statements = []

        if not self.match("LBRACE"):
            return None


        while self.peek().token_type != "RBRACE" and self.peek().token_type != "EOF":
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
  
                break

        self.match("RBRACE")
        return BlockStatement(statements)

    def parse_expression(self):
  
        left = self.parse_term()
        if left is None: return None
        
  
        while self.peek().token_type == "OPERATOR" and self.peek().value in ["+", "-", "==", "!=", "<", ">", "<=", ">="]:
            op = self.peek().value
            self.advance() # Consume operator
            
  
            right = self.parse_term()
            
  
            left = Expressions(left, op, right)
            
        return left

    def parse_term(self):
  
        left = self.parse_factor()
        if left is None: return None
        
        
        while self.peek().token_type == "OPERATOR" and self.peek().value in ["*", "/", "%"]:
            op = self.peek().value
            self.advance() 
            
            right = self.parse_factor()
            left = Expressions(left, op, right)
            
        return left

    def parse_factor(self):
        token = self.peek()
        
  
        if token.token_type in ["INTEGER", "FLOAT", "IDENTIFIER", "STRING"]:
            self.advance()
            return token.value 
            
  
        elif token.token_type == "LPAREN":
            self.advance() 
            expr = self.parse_expression()
            
            if self.peek().token_type == "RPAREN":
                self.advance() 
                return expr
            else:
                self.errors.append("Expected ')' after expression")
                return None
                
        else:
            self.errors.append(f"Unexpected token in math expression: {token.value}")
            return None


    def parse_if(self):
        self.match("KEYWORD") # consumes 'etha'

        if self.peek().token_type == "LPAREN":
            self.advance()
        else:
            self.errors.append("Expected: (")
            return None

        condition = self.parse_expression()
        if condition == None:
            return None

        if self.peek().token_type == "RPAREN":
            self.advance()
        else:
            self.errors.append("Expected: )")
            return None

        body = self.parse_statement()
        else_body = None

        
        
        if self.peek().token_type == "KEYWORD" and self.peek().value == "aw":
            self.advance() # Consume 'aw'
            
        
            if self.peek().token_type == "KEYWORD" and self.peek().value == "etha":
                else_body = self.parse_if() 
            else:
        
                else_body = self.parse_statement()

        return IfStatement(condition, body, else_body)
    
    def parse_for(self):
        self.match("KEYWORD") # matches 'lkol'

        
        if not self.match("LPAREN"): 
            return None

        
        if self.peek().token_type == "KEYWORD":
            init = self.parse_declaration() 
        else:
            init = self.parse_assignment(require_semicolon=True)

        if init is None: return None

        
        condition = self.parse_expression()
        if condition is None: return None

        
        if not self.match("SEMICOLON"): 
            return None

        
        update = self.parse_assignment(require_semicolon=False)
        if update is None: return None

        
        if not self.match("RPAREN"): 
            return None

        
        body = self.parse_statement()

        return ForStatement(init, condition, update, body)





    def parse_statement(self):
        token = self.peek()
        
        # 0. Blocks {}
        if token.token_type == "LBRACE":
            return self.parse_block()
        
        # assignment
        if token.token_type == "IDENTIFIER":
            return self.parse_assignment()
        
        # 1. Variable Declarations
        if token.value in ["sahih", "kasr", "kalema", "manteq"]:
            return self.parse_declaration()
            
        # 2. Control Flow & Blocks
        elif token.value == "etha": return self.parse_if()
        elif token.value == "talama": return self.parse_while()
        elif token.value == "lkol": return self.parse_for()
        
        
        # 3. I/O and Actions
        elif token.value == "itba3": return self.parse_print()
        elif token.value == "da5el": return self.parse_input()
        
        # 4. Program Flow
        elif token.value == "raje3": return self.parse_return()
        elif token.value == "waqef": return self.parse_break()
        elif token.value == "kammel": return self.parse_continue()
        
        
        # 5. Functions
        elif token.value == "shoghol": return self.parse_function()
        
        # 6. Fallback/Error
        else:
            self.errors.append(f"Unknown statement starting with: {token.value}")
            self.advance()
            return None

    def parse(self):
        while self.peek().token_type != "EOF":
            # The entry point uses the router
            stmt = self.parse_statement()
            if stmt:
                self.ast.append(stmt)
        return self.ast, self.errors

#===============================================================================================================

# main:
code = """

    shoghol main() 
    {    
        lkol (sahih i = 0; i < x; i = i + 1) 
        {
            etha (x != 99) {
                raje3;
            }
        }

        etha (x > 5) {
            itba3("High");
        } aw etha (x > 2) {
            itba3("Medium");
        } aw {
            itba3("Low");
        }
    }

"""

tokens, lexical_errors = lexer(code)

for token in tokens:
    print(token)

parser = Parser(tokens)

ast, errors = parser.parse()

print("AST:")
for node in ast:
    print(node)

print("\nErrors:")
print(errors)