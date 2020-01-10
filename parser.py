from errors import InvalidSyntaxError
from constants import Constants

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start=self.tok.pos_start
        self.pos_end=self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class BinaryOperatorNode:
    def __init__(self, left_node, operator, right_node):
        self.left_node = left_node
        self.right_node = right_node
        self.operator = operator

        self.pos_start=self.left_node.pos_start
        self.pos_end=self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.operator}, {self.right_node})'


class UnaryOperatorNode:
    def __init__(self, operator, node):
        self.operator = operator
        self.node = node

        self.pos_start= self.operator.pos_start
        self.pos_end= self.node.pos_end
    
    def __repr__(self):
        return f'{self.operator}:{self.node}'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end



class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end


class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node

        self.pos_start= self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start= self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_name_toks=  arg_name_toks
        self.body_node = body_node

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks)>0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        
        self.pos_end = self.body_node.pos_end



class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes)>0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes)-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end







class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count=0

    def register_advancement(self):
        self.advance_count+=1

    def register(self, res):
        self.advance_count+=res.advance_count
        if res.error:
            self.error=res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count==0:
            self.error = error
        return self










class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok


    def parse(self):
        res = self.expr()

        if not res.error and self.current_tok.type!=Constants.TOK_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected +, -, * or /'
            ))
        return res

    def atom(self):
        res= ParseResult()
        tok = self.current_tok
        
        if tok.type == Constants.TOK_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))


        elif tok.type in (Constants.TOK_INT, Constants.TOK_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        

        elif tok.type == Constants.TOK_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())

            if res.error:
                return res
            if self.current_tok.type == Constants.TOK_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected \')\''
                ))

        
        elif tok.matches(Constants.TOK_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(Constants.TOK_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(Constants.TOK_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(Constants.TOK_KEYWORD, 'func'):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)
        

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            'Expected int, float, +, -, *, /. keywords - if, for, while, func etc.'
        ))


    def power(self):
        return self.binary_operation(self.call,(Constants.TOK_POW,), self.factor)


    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == Constants.TOK_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == Constants.TOK_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"
                    ))

                while self.current_tok.type == Constants.TOK_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != Constants.TOK_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)






            
        
    
    def factor(self):
        res= ParseResult()
        tok = self.current_tok

        if tok.type in (Constants.TOK_PLUS, Constants.TOK_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOperatorNode(tok, factor))
        return self.power()

    def term(self):
        return self.binary_operation(self.factor, (Constants.TOK_MULTIPLY, Constants.TOK_DIVIDE))

    def expr(self):
        res = ParseResult()

        ### New variable declaration
        if self.current_tok.matches(Constants.TOK_KEYWORD, 'var'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != Constants.TOK_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected Identifier'
                ))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type != Constants.TOK_EQUALS:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected \'=\''
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())

            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.binary_operation(self.comp_expr, ((Constants.TOK_KEYWORD, 'and'), (Constants.TOK_KEYWORD, 'or'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'var\', int, float, identifier or operator or keywords'
            ))

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()
        if self.current_tok.matches(Constants.TOK_KEYWORD, 'not'):
            operator = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())

            if res.error:
                return res
            return res.success(UnaryOperatorNode(operator, node))

        node = res.register(self.binary_operation(
            self.arith_expr,
                (Constants.TOK_EE,
                Constants.TOK_NE,
                Constants.TOK_LT,
                Constants.TOK_GT,
                Constants.TOK_LTE,
                Constants.TOK_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected int, float, identifier, operators'
            ))

        return res.success(node)


    def arith_expr(self):
        return self.binary_operation(self.term, (Constants.TOK_PLUS, Constants.TOK_MINUS))

    def binary_operation(self,func_a, ops, func_b=None):
        if func_b == None:
            func_b=func_a
        
        res= ParseResult()
        leftn = res.register(func_a())
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            operator = self.current_tok
            res.register_advancement()
            self.advance()
            rightn = res.register(func_b())
            if res.error:
                return res
            leftn = BinaryOperatorNode(leftn, operator, rightn)
        return res.success(leftn)


    def if_expr(self):
	    res = ParseResult()
	    cases = []
	    else_case = None

	    if not self.current_tok.matches(Constants.TOK_KEYWORD, 'if'):
	    	return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'if'"
			))

	    res.register_advancement()
	    self.advance()

	    condition = res.register(self.expr())
	    if res.error: return res

	    if not self.current_tok.matches(Constants.TOK_KEYWORD, 'then'):
        	return res.failure(InvalidSyntaxError(
	    		self.current_tok.pos_start, self.current_tok.pos_end,
	    		f"Expected 'then'"
	    	))

	    res.register_advancement()
	    self.advance()

	    expr = res.register(self.expr())
	    if res.error: return res
	    cases.append((condition, expr))

	    while self.current_tok.matches(Constants.TOK_KEYWORD, 'elseif'):
	    	res.register_advancement()
	    	self.advance()

	    	condition = res.register(self.expr())
	    	if res.error: return res

	    	if not self.current_tok.matches(Constants.TOK_KEYWORD, 'then'):
	    		return res.failure(InvalidSyntaxError(
	    			self.current_tok.pos_start, self.current_tok.pos_end,
	    			f"Expected 'then'"
	    		))

	    	res.register_advancement()
	    	self.advance()

	    	expr = res.register(self.expr())
	    	if res.error: return res
	    	cases.append((condition, expr))

	    if self.current_tok.matches(Constants.TOK_KEYWORD, 'else'):
	    	res.register_advancement()
	    	self.advance()

	    	else_case = res.register(self.expr())
	    	if res.error: return res

	    return res.success(IfNode(cases, else_case))

    

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Constants.TOK_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'for\''
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != Constants.TOK_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected identifier'
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != Constants.TOK_EQUALS:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'=\''
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res
        
        if not self.current_tok.matches(Constants.TOK_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'to\''
            ))
        
        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(Constants.TOK_KEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res

        else:
            step_value = None

        if not self.current_tok.matches(Constants.TOK_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'then\''
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    
    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(Constants.TOK_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'while\''
            ))
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(Constants.TOK_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'then\''
            ))
        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))


    
    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(Constants.TOK_KEYWORD, 'func'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected keyword \'func\''
            ))
        res.register_advancement()
        self.advance()

        if self.current_tok.type == Constants.TOK_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != Constants.TOK_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected parantheses \'(\''
                ))
        else:
            var_name_tok = None
            if self.current_tok.type != Constants.TOK_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected parantheses \'(\''
                ))

        res.register_advancement()
        self.advance()

        arg_name_toks =  []

        if self.current_tok.type == Constants.TOK_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == Constants.TOK_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != Constants.TOK_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        'Expected Identifier'
                    ))
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
            
            if self.current_tok.type != Constants.TOK_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected \',\' or \')\''
                ))
        else:
            if self.current_tok.type != Constants.TOK_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    'Expected identifier or \')\''
                ))
        res.register_advancement()
        self.advance()

        if self.current_tok.type != Constants.TOK_ARROW:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                'Expected \'->\''
            ))
        res.register_advancement()
        self.advance()

        node_to_return = res.register(self.expr())
        if res.error:
            return res

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return))
            