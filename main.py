from lexer import Lexer
from parser import Parser
from interpreter import Context, Interpreter, SymbolTable, Number

global_symbol_table = SymbolTable()
global_symbol_table.set('null', Number(0))
global_symbol_table.set('true', Number(1))
global_symbol_table.set('false', Number(0))

def run(fname, text):
    lexer = Lexer(fname, text)
    tokens, errors = lexer.gen_tokens() 

    if errors:
        return None, errors

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error


def main():
    while True:
        text = input('hash/> ')
        result, error = run('<stdin>',text)

        if error:
            print(error.as_string())
        
        else:
            print(result)



'''
Start the Program
'''
if __name__=='__main__':
    main()