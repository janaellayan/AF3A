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
    def __init__(self, var_type, name, value):
        self.var_type = var_type
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

        
        var_type=self.peek().value
        self.match("KEYWORD")

        
        if self.peek().token_type != "IDENTIFIER":
            self.syntax_error("Expected variable name after type keyword")
            return

        name = self.peek().value
        self.advance()

        
        if self.peek().token_type == "OPERATOR" and self.peek().value == "=":
            self.advance()
        else:
            self.syntax_error("Missing '=' in variable declaration")
            return

        
        value = self.parse_expression()
        if value is None:
            return

        
        if self.peek().token_type == "SEMICOLON":
            self.advance()
        else:
            self.syntax_error("Missing semicolon ';' after declaration")
            return

        
        return VarDeclaration(name, value)








    def parse_print(self):#this is new
        
        self.match("KEYWORD") #checks expexted

        if self.peek().token_type != "LPAREN":
            self.syntax_error("Expected '('")
            return
        else:
            self.advance()
        
    

        if self.peek().token_type == "STRING" or self.peek().token_type == "INTEGER" or self.peek().token_type == "FLOAT" or self.peek().token_type == "IDENTIFIER":
            value = self.peek().value
            self.advance()
        else:
            self.syntax_error("Expected argument types: STRING or INTEGER or FLOAT or IDENTIFIER")
            return
        
        

        if self.peek().token_type != "RPAREN":
            self.syntax_error("Expected ')'")
            return
        else:
            self.advance()
        
        
        if self.peek().token_type != "SEMICOLON":
            self.syntax_error("Expected ';' after print statement")
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
            self.syntax_error("Expected function name")
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
            self.syntax_error("Expected '('")
            return 
        else:
            self.advance()
        
        condition = self.parse_expression()
        if condition == None:
            return None
        
            


        
        if self.peek().token_type != "RPAREN":
            self.syntax_error("Expected ')'")
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
            self.syntax_error("Expected '=' in assignment")
            return None

        value = self.parse_expression()
        if value is None:
            return None


        if require_semicolon:
            if self.peek().token_type == "SEMICOLON":
                self.advance()
            else:
                self.syntax_error("Expected ';' after assignment")
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
        
  
        if token.token_type in ["INTEGER", "FLOAT", "IDENTIFIER", "STRING"] or token.value in ["sa7", "ghalat"]:
            self.advance()
            return token.value 
            
  
        elif token.token_type == "LPAREN":
            self.advance() 
            expr = self.parse_expression()
            
            if self.peek().token_type == "RPAREN":
                self.advance() 
                return expr
            else:
                self.syntax_error("Expected ')' after expression")
                return None
                
        else:
            self.syntax_error(f"Unexpected token in math expression: {token.value}")
            return None


    def parse_if(self):
        self.match("KEYWORD") # consumes 'etha'

        if self.peek().token_type == "LPAREN":
            self.advance()
        else:
            self.syntax_error("Expected: (")
            return None

        condition = self.parse_expression()
        if condition == None:
            return None

        if self.peek().token_type == "RPAREN":
            self.advance()
        else:
            self.syntax_error("Expected: )")
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
            self.syntax_error(f"Unknown statement starting with: {token.value}")
            self.advance()
            return None

    def parse(self):
        while self.peek().token_type != "EOF":
            # The entry point uses the router
            stmt = self.parse_statement()
            if stmt:
                self.ast.append(stmt)
            else: 
                self.synchronize()
        return self.ast, self.errors


class Symbol:
    def __init__(self, name, symbol_type, scope):
        self.name = name
        self.symbol_type = symbol_type
        self.scope = scope

    def __repr__(self):
        return f"{self.name} | type: {self.symbol_type} | scope: {self.scope}"


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = []
        self.errors = []
        self.scope = "global"
        self.in_loop = 0
        self.in_function = 0

    def semantic_error(self, message):
        self.errors.append(
            CompilerError(
                "Semantic Error",
                message,
                0,
                0
            )
        )

    def lookup(self, name):
        for symbol in reversed(self.symbol_table):
            if symbol.name == name and symbol.scope in [self.scope, "global"]:
                return symbol
        return None

    def exists_in_current_scope(self, name):
        for symbol in self.symbol_table:
            if symbol.name == name and symbol.scope == self.scope:
                return True
        return False

    def add_symbol(self, name, symbol_type):
        if self.exists_in_current_scope(name):
            self.semantic_error(f"Variable '{name}' is already declared in this scope")
            return

        self.symbol_table.append(Symbol(name, symbol_type, self.scope))

    def infer_type(self, value):
        if isinstance(value, Expressions):
            left_type = self.infer_type(value.arg1)
            right_type = self.infer_type(value.arg2)

            if value.exp in ["==", "!=", "<", ">", "<=", ">="]:
                return "manteq"

            if value.exp in ["+", "-", "*", "/", "%"]:
                if left_type == "kalema" or right_type == "kalema":
                    self.semantic_error("Cannot use math operators with kalema/string values")
                    return "unknown"

                if left_type == "kasr" or right_type == "kasr":
                    return "kasr"

                if left_type == "sahih" and right_type == "sahih":
                    return "sahih"

            return "unknown"

        value = str(value)

        if value.startswith('"') and value.endswith('"'):
            return "kalema"

        if value in ["sa7", "ghalat"]:
            return "manteq"

        if "." in value and value.replace(".", "", 1).isdigit():
            return "kasr"

        if value.isdigit():
            return "sahih"

        symbol = self.lookup(value)
        if symbol:
            return symbol.symbol_type

        self.semantic_error(f"Variable '{value}' used before declaration")
        return "unknown"

    def types_compatible(self, declared_type, value_type):
        if value_type == "unknown":
            return True

        if declared_type == value_type:
            return True

        if declared_type == "kasr" and value_type == "sahih":
            return True

        return False

    def analyze_statement(self, node):
        if isinstance(node, VarDeclaration):
            value_type = self.infer_type(node.value)

            if not self.types_compatible(node.var_type, value_type):
                self.semantic_error(
                    f"Cannot assign {value_type} to variable '{node.name}' of type {node.var_type}"
                )

            self.add_symbol(node.name, node.var_type)

        elif isinstance(node, AssignmentStatement):
            symbol = self.lookup(node.name)

            if not symbol:
                self.semantic_error(f"Variable '{node.name}' assigned before declaration")
                return

            value_type = self.infer_type(node.value)

            if not self.types_compatible(symbol.symbol_type, value_type):
                self.semantic_error(
                    f"Cannot assign {value_type} to variable '{node.name}' of type {symbol.symbol_type}"
                )

        elif isinstance(node, PrintStatement):
            self.infer_type(node.value)

        elif isinstance(node, InputStatement):
            if not self.lookup(node.name):
                self.semantic_error(f"Input variable '{node.name}' used before declaration")

        elif isinstance(node, IfStatement):
            condition_type = self.infer_type(node.condition)

            if condition_type != "manteq":
                self.semantic_error("If condition must be a boolean/manteq expression")

            self.analyze_statement(node.body)

            if node.else_body:
                self.analyze_statement(node.else_body)

        elif isinstance(node, WhileStatement):
            condition_type = self.infer_type(node.condition)

            if condition_type != "manteq":
                self.semantic_error("While condition must be a boolean/manteq expression")

            self.in_loop += 1
            self.analyze_statement(node.body)
            self.in_loop -= 1

        elif isinstance(node, ForStatement):
            self.in_loop += 1

            self.analyze_statement(node.init)

            condition_type = self.infer_type(node.condition)
            if condition_type != "manteq":
                self.semantic_error("For condition must be a boolean/manteq expression")

            self.analyze_statement(node.update)
            self.analyze_statement(node.body)

            self.in_loop -= 1

        elif isinstance(node, BlockStatement):
            for statement in node.statements:
                self.analyze_statement(statement)

        elif isinstance(node, BreakStatement):
            if self.in_loop == 0:
                self.semantic_error("'waqef' used outside a loop")

        elif isinstance(node, ContinueStatement):
            if self.in_loop == 0:
                self.semantic_error("'kammel' used outside a loop")

        elif isinstance(node, ReturnStatement):
            if self.in_function == 0:
                self.semantic_error("'raje3' used outside a function")

        elif isinstance(node, FunctionDeclaration):
            old_scope = self.scope
            self.scope = node.name
            self.in_function += 1

            self.analyze_statement(node.body)

            self.in_function -= 1
            self.scope = old_scope

    def analyze(self, ast):
        for node in ast:
            self.analyze_statement(node)

        return self.symbol_table, self.errors

#===============================================================================================================

# main:
code = """
shoghol main() {
    sahih x = 5;
    kasr y = 3.2;
    kalema message = "Done";
    manteq check = sa7;

    lkol (sahih i = 0; i < x; i = i + 1) {
        etha (i == 3) {
            waqef;
        } aw {
            itba3(message);
        }
    }

    raje3;
}
"""

tokens, lexical_errors = lexer(code)

for token in tokens:
    print(token)

parser = Parser(tokens)

ast, errors = parser.parse()

semantic_analyzer = SemanticAnalyzer()
symbol_table, semantic_errors = semantic_analyzer.analyze(ast)

print("AST:")
for node in ast:
    print(node)

print("\nSymbol Table:")
for symbol in symbol_table:
    print(symbol)

print("\nLexical Errors:")
for error in lexical_errors:
    print(error)

print("\nSyntax Errors:")
for error in errors:
    print(error)

print("\nSemantic Errors:")
for error in semantic_errors:
    print(error)