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
        self.value=None
        self.error=None
    
    def register(self, res):
        if res.error:
            self.error=res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
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
            error_name = 'Runtime Error',
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
                    error_name='Runtime Error',
                    details='Division by zero',
                    context=self.context
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


class Function(Value):
    def __init__(self, name, body_node, arg_names):
        super().__init__()
        self.name = name or '<unnamed>'
        self.body_node =body_node
        self.arg_names = arg_names
    
    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()

        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args)>len(self.arg_names):
            return res.failure(RTError(
                'Runtime Error',
                self.pos_start, self.pos_end,
                f'{len(args) - len(self.arg_names)} more arguments passed into {self.name}',
                self.context
            ))
        if len(args)<len(self.arg_names):
            return res.failure(RTError(
                'Runtime Error',
                self.pos_start, self.pos_end,
                f'{len(self.arg_names) - len(args)} less arguments passed into {self.name}',
                self.context
            ))
        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value) 

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f'<func> {self.name}'
        

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
                error_name= 'Runtime Error',
                details= details,
                context=context
            ))
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value

        value = res.register(self.visit(node.value_node, context))

        if res.error:
            return res
        context.symbol_table.set(var_name, value)
        return res.success(value)


    def visit_IfNode(self, node, context):
        res = RuntimeResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))

                if res.error:
                    return res
                return res.success(expr_value)
            
            
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)


    def visit_ForNode(self, node, context):
        res = RuntimeResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error:
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

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break
            res.register(self.visit(node.body_node, context))
        return res.success(None)


    def visit_FuncDefNode(self, node, context):
        res = RuntimeResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names= [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)
        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res= RuntimeResult()

        args= []

        value_to_call = res.register(self.visit(node.node_to_call,context))
        if res.error:
            return res
        
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error:
                return res
        
        return_value = res.register(value_to_call.execute(args))
        if res.error:
            return res

        return res.success(return_value)