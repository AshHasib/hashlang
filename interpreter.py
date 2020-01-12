from errors import RTError
from constants import Constants





class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent=parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None







class RuntimeResult:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.value=None
        self.error=None
        self.func_return_value = None
        self.loop_should_continue =False
        self.loop_should_break = False
    
    def register(self, res):    
        self.error=res.error
        self.func_return_value = res.func_return_value
        self.loop_should_break = res.loop_should_break
        self.loop_should_continue = res.loop_should_continue
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self
    
    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def should_return(self):
        return (
        self.error or
        self.func_return_value or
        self.loop_should_continue or
        self.loop_should_break
    )

    def failure(self, error):
        self.reset()
        self.error= error
        return self
        





class SymbolTable:
    def __init__(self, parent= None):
        self.symbols = {}
        self.parent = parent

    def get(self, var_name):
        value = self.symbols.get(var_name, None)
        if value == None and self.parent:
            return self.parent.get(var_name)
        return value

    def set(self, name, value):
        self.symbols[name]=value

    def remove(self, name):
        del self.symbols[name]






class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start=pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context=context
        return self
    
    def added_to(self, another):
        return None, self.illegal_operation(another)

    def subtracted_by(self, another):
        return None, self.illegal_operation(another)

    def multiplied_by(self, another):
        return None, self.illegal_operation(another)

    def divided_by(self, another):
        return None, self.illegal_operation(another)

    def powered_by(self, another):
        return None, self.illegal_operation(another)

    def compare_equals(self, another):
        return None, self.illegal_operation(another)
    def compare_not_equals(self, another):
        return None, self.illegal_operation(another)
    def compare_lt(self, another):
        return None, self.illegal_operation(another)
    def compare_gt(self, another):
        return None, self.illegal_operation(another)
    def compare_lte(self, another):
        return None, self.illegal_operation(another)
    def compare_gte(self, another):
        return None, self.illegal_operation(another)

    def and_to(self, another):
        return None, self.illegal_operation(another)
    def or_to(self, another):
        return None, self.illegal_operation(another)

    def notted(self, another):
        return None, self.illegal_operation(another)
    

    def illegal_operation(self, another = None):
        if not another:
            another = self
        return RTError(
            pos_start =self.pos_start, pos_end=self.pos_end,
            details= 'Illegal Operation',
            context = self.context
        )



class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def added_to(self, num):
        if isinstance(num, Number):
            return Number(self.value+num.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)

    def subtracted_by(self, num):
        if isinstance(num, Number):
            return Number(self.value-num.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)

    def multiplied_by(self, num):
        if isinstance(num, Number):
            return Number(self.value*num.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)

    def divided_by(self, num):
        if isinstance(num, Number):
            if num.value == 0:
                return None, RTError(
                    num.pos_start, num.pos_end,
                    'Division by zero',
                    self.context
                )
            return Number(self.value/num.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)

    def powered_by(self, num):
        if isinstance(num, Number):
            return Number(self.value ** num.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)

    def compare_equals(self, num):
        if isinstance(num, Number):
            return Number(int(self.value == num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    def compare_not_equals(self, num):
        if isinstance(num, Number):
            return Number(int(self.value != num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)

    def compare_lt(self, num):
        if isinstance(num, Number):
            return Number(int(self.value < num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    def compare_gt(self, num):
        if isinstance(num, Number):
            return Number(int(self.value > num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    def compare_lte(self, num):
        if isinstance(num, Number):
            return Number(int(self.value <= num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    def compare_gte(self, num):
        if isinstance(num, Number):
            return Number(int(self.value >= num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    def and_to(self, num):
        if isinstance(num, Number):
            return Number(int(self.value and num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    
    def or_to(self, num):
        if isinstance(num, Number):
            return Number(int(self.value or num.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, num)
    def notted(self, num):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

############################ CREATING SOME CONSTANTS
Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)
####################################################


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f'"{self.value}"'





class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()

        if len(args) > len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)















class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res
        
        ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
        return res.success(ret_value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"





class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RuntimeResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return():
            return res
        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"



    ############### Functions ##################
    
    def execute_output(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RuntimeResult().success(Number.null)
    execute_output.arg_names = ['value']
    
    def execute_echo(self, exec_ctx):
        return RuntimeResult().success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_echo.arg_names = ['value']
    
    def execute_getline(self, exec_ctx):
        text = input()
        return RuntimeResult().success(String(text))
    execute_getline.arg_names = []

    def execute_getnum(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RuntimeResult().success(Number(number))
    execute_getnum.arg_names = []

    def execute_clear(self, exec_ctx):
        import os, platform
        os.system('cls' if platform.system() == 'Windows' else 'clear') 
        return RuntimeResult().success(Number.null)
    execute_clear.arg_names = []
    
    
    def execute_isnum(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_isnum.arg_names = ["value"]

    def execute_isstr(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_isstr.arg_names = ["value"]

    def execute_islist(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), LinkedList)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_islist.arg_names = ["value"]

    def execute_isfunc(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RuntimeResult().success(Number.true if is_number else Number.false)
    execute_isfunc.arg_names = ["value"]

        
    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, LinkedList):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RuntimeResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, LinkedList):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))
        return RuntimeResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, LinkedList):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, LinkedList):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RuntimeResult().success(Number.null)
    execute_extend.arg_names = ["listA", "listB"]
    
    
    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, LinkedList):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Argument must be list",
                exec_ctx
            ))

        return RuntimeResult().success(Number(len(list_.elements)))
    execute_len.arg_names = ["list"]
    
    
    
    def execute_run(self, exec_ctx):
        import main
        fn = exec_ctx.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be string",
                exec_ctx
            ))

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script \"{fn}\"\n" + str(e),
                exec_ctx
            ))

        _, error = main.run(fn, script)
        
        if error:
            return RuntimeResult().failure(RTError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script \"{fn}\"\n" +
                error.as_string(),
                exec_ctx
            ))

        return RuntimeResult().success(Number.null)
    execute_run.arg_names = ["fn"]
    
    

BuiltInFunction.print       = BuiltInFunction("output")
BuiltInFunction.print_ret   = BuiltInFunction("echo")
BuiltInFunction.input       = BuiltInFunction("getline")
BuiltInFunction.input_int   = BuiltInFunction("getnum")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("isnum")
BuiltInFunction.is_string   = BuiltInFunction("isstr")
BuiltInFunction.is_list     = BuiltInFunction("islist")
BuiltInFunction.is_function = BuiltInFunction("isfunc")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.run      = BuiltInFunction("run")
BuiltInFunction.length      = BuiltInFunction("length")




class LinkedList(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subtracted_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                other.pos_start, other.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multiplied_by(self, other):
        if isinstance(other, LinkedList):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def divided_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                other.pos_start, other.pos_end,
                'Element at this index could not be retrieved from list because index is out of bounds',
                self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = LinkedList(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    
    def __str__(self):
        return f'{", ".join([str(x) for x in self.elements])}'

    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'










class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node,context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self,node, context):
        return RuntimeResult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end))
    
    def visit_BinaryOperatorNode(self, node, context):
        rtresult = RuntimeResult()

        left= rtresult.register(self.visit(node.left_node, context))
        right = rtresult.register(self.visit(node.right_node, context))

        if rtresult.error:
            return rtresult

        if node.operator.type == Constants.TOK_PLUS:
            result, error = left.added_to(right)

        elif node.operator.type == Constants.TOK_MINUS:
            result, error = left.subtracted_by(right)

        elif node.operator.type == Constants.TOK_MULTIPLY:
            result, error = left.multiplied_by(right)
        
        elif node.operator.type == Constants.TOK_DIVIDE:
            result, error = left.divided_by(right)

        elif node.operator.type == Constants.TOK_POW:
            result, error = left.powered_by(right)
        

        # COMPARISIONS
        elif node.operator.type == Constants.TOK_EE:
            result, error = left.compare_equals(right)
        elif node.operator.type == Constants.TOK_NE:
            result, error = left.compare_not_equals(right)
        elif node.operator.type == Constants.TOK_LT:
            result, error = left.compare_lt(right)
        elif node.operator.type == Constants.TOK_GT:
            result, error = left.compare_gt(right)
        elif node.operator.type == Constants.TOK_LTE:
            result, error = left.compare_lte(right)
        elif node.operator.type == Constants.TOK_GTE:
            result, error = left.compare_gte(right)
        elif node.operator.matches(Constants.TOK_KEYWORD, 'and'):
            result, error = left.and_to(right)
        elif node.operator.matches(Constants.TOK_KEYWORD, 'or'):
            result, error = left.or_to(right)
        

        if error:
            return rtresult.failure(error)
        else:
            return rtresult.success(result.set_pos(node.pos_start, node.pos_end))


    def visit_UnaryOperatorNode(self, node, context):
        rtresult = RuntimeResult()
        num = rtresult.register(self.visit(node.node, context))

        if node.operator.type == Constants.TOK_MINUS:
            num, error= num.multiplied_by(Number(-1))
        elif node.operator.matches(Constants.TOK_KEYWORD, 'not'):
            num, error = num.notted()
            
        if error:
            return rtresult.failure(error)
        else:   
            return rtresult.success(num.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            details = f"\'{var_name}\' is not defined"
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                details,
                context
            ))
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value

        value = res.register(self.visit(node.value_node, context))

        if res.should_return():
            return res
        context.symbol_table.set(var_name, value)
        return res.success(value)


    def visit_IfNode(self, node, context):
        res = RuntimeResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))

                if res.should_return():
                    return res
                return res.success(Number.null if should_return_null else expr_value)
            
            
        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(Number.null if should_return_null else expr_value)

        return res.success(Number.null)


    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []
        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return():
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value>=0:
            condition = lambda: i< end_value.value
        else:
            condition = lambda: i> end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i+=step_value.value

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res
            
            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break
            elements.append(value)

        return res.success(Number.null if node.should_return_null else LinkedList(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()
        elements= []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res

            if not condition.is_true():
                break
            value = res.register(self.visit(node.body_node, context))
            
            if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False:
                return res
            
            if res.loop_should_continue:
                continue
            
            if res.loop_should_break:
                break
            elements.append(value)
    
        return res.success(Number.null if node.should_return_null else LinkedList(elements).set_context(context).set_pos(node.pos_start, node.pos_end))


    def visit_FuncDefNode(self, node, context):
        res = RuntimeResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names= [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)
        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res= RuntimeResult()

        args= []

        value_to_call = res.register(self.visit(node.node_to_call,context))
        if res.should_return():
            return res
        
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res
        
        return_value = res.register(value_to_call.execute(args))
        if res.should_return():
            return res
        
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)
    
    def visit_StringNode(self, node, context):
        return RuntimeResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
    
    
    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return(): return res

        return res.success(
            LinkedList(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_ReturnNode(self, node, context):
        res = RuntimeResult()
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return():
                return res
        else:
            value = Number.null
        
        return res.success_return(value)
    
    def visit_ContinueNode(self, node, context):
        return RuntimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RuntimeResult().success_break()