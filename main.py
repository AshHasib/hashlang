from lexer import Lexer
from parser import Parser
from interpreter import Context, Interpreter, SymbolTable, Number
from interpreter import BuiltInFunction
global_symbol_table = SymbolTable()
global_symbol_table.set('null', Number.null)
global_symbol_table.set('true', Number.true)
global_symbol_table.set('false', Number.false)
global_symbol_table.set("output", BuiltInFunction.print)
global_symbol_table.set("echo", BuiltInFunction.print_ret)
global_symbol_table.set("getline", BuiltInFunction.input)
global_symbol_table.set("getnum", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
#lobal_symbol_table.set("CLS", BuiltInFunction.clear)
global_symbol_table.set("isnum", BuiltInFunction.is_number)
global_symbol_table.set("isstr", BuiltInFunction.is_string)
global_symbol_table.set("islist", BuiltInFunction.is_list)
global_symbol_table.set("isfunc", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)









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
        
        elif result:
            print(result)



'''
Start the Program
'''
if __name__=='__main__':
    main()