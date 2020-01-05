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
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, var_name):
        value = self.symbols.get(var_name, None)
        if value == None and self.parent:
            return self.parent.get(var_name)
        return value

    def set(self, name, value):
        self.symbols[name]=value

    def remove(self, name):
        del self.symbols[name]



class Number:
    def __init__(self, value):
        self.value= value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start=pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context=context
        return self
    
    def added_to(self, num):
        if isinstance(num, Number):
            return Number(self.value+num.value).set_context(self.context), None

    def subtracted_by(self, num):
        if isinstance(num, Number):
            return Number(self.value-num.value).set_context(self.context), None

    def multiplied_by(self, num):
        if isinstance(num, Number):
            return Number(self.value*num.value).set_context(self.context), None

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

    def powered_by(self, num):
        if isinstance(num, Number):
            return Number(self.value ** num.value).set_context(self.context), None

    def compare_equals(self, num):
        if isinstance(num, Number):
            return Number(int(self.value == num.value)).set_context(self.context), None
    def compare_not_equals(self, num):
        if isinstance(num, Number):
            return Number(int(self.value != num.value)).set_context(self.context), None
    def compare_lt(self, num):
        if isinstance(num, Number):
            return Number(int(self.value < num.value)).set_context(self.context), None
    def compare_gt(self, num):
        if isinstance(num, Number):
            return Number(int(self.value > num.value)).set_context(self.context), None
    def compare_lte(self, num):
        if isinstance(num, Number):
            return Number(int(self.value <= num.value)).set_context(self.context), None
    def compare_gte(self, num):
        if isinstance(num, Number):
            return Number(int(self.value >= num.value)).set_context(self.context), None

    def and_to(self, num):
        if isinstance(num, Number):
            return Number(int(self.value and num.value)).set_context(self.context), None
    def or_to(self, num):
        if isinstance(num, Number):
            return Number(int(self.value or num.value)).set_context(self.context), None

    def notted(self, num):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    

    def __repr__(self):
        return str(self.value)


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