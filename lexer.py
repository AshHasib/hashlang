from errors import Error, IllegalCharError, ExpectedCharError
from constants import Constants

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type=type_
        self.value=value

        if pos_start:
            self.pos_start=pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end=  pos_end

    def matches(self, type_, value):
        return self.type==type_ and self.value==value 

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'



class Position:
    def __init__(self, idx, ln, col,fname, ftext):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fname = fname
        self.ftext = ftext

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self
    
    def copy(self):
        return Position (self.idx, self.ln, self.col, self.fname, self.ftext)



class Lexer:
    def __init__(self, fname, text):
        self.fname= fname
        self.text=text
        self.pos=Position(-1,0,-1,fname, text)
        self.current_char=None
        self.advance()
    
    ### GO FORWARD ###
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char=self.text[self.pos.idx] if self.pos.idx<len(self.text) else None


    def gen_tokens(self):
        tokens=[]

        while self.current_char!=None:
            if self.current_char in ' \t':
                self.advance()

            elif self.current_char in Constants.LETTERS:
                tokens.append(self.gen_identifier())

            elif self.current_char in Constants.DIGITS:
                tokens.append(self.gen_number())
        
            elif self.current_char == '+':
                tokens.append(Token(Constants.TOK_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.gen_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(Constants.TOK_MULTIPLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(Constants.TOK_DIVIDE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(Constants.TOK_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                tok, error = self.gen_not_equals()
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == '=':
                tokens.append(self.gen_equals())
            elif self.current_char == '<':
                tokens.append(self.gen_less_than())
            elif self.current_char == '>':
                tokens.append(self.gen_greater_than())
                
            elif self.current_char == '(':
                tokens.append(Token(Constants.TOK_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(Constants.TOK_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(Constants.TOK_COMMA, pos_start=self.pos))
                self.advance()
            


            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,'\''+char+'\'')
        tokens.append(Token(Constants.TOK_EOF, pos_start=self.pos))
        return tokens, None



    def gen_number(self):
        num_str = ''
        dot_count=0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in Constants.DIGITS + '.':
            if self.current_char == '.':
                if dot_count==1:
                    break
                dot_count+=1
                num_str+='.'
            else:
                num_str+=self.current_char
            self.advance()
            
        if dot_count==0:
            return Token(Constants.TOK_INT, int(num_str), pos_start=pos_start, pos_end= self.pos)
        else:
            return Token(Constants.TOK_FLOAT, float(num_str), pos_start=pos_start, pos_end= self.pos)


    def gen_identifier(self):
        id_str=''
        pos_start=self.pos.copy()

        LETTERS_DIGITS=Constants.LETTERS+Constants.DIGITS

        while self.current_char!=None and self.current_char in LETTERS_DIGITS +'_':
            id_str+= self.current_char
            self.advance()
        
        tok_type = Constants.TOK_KEYWORD if id_str in Constants.LIST_KEYWORDS else Constants.TOK_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)



    def gen_not_equals(self):
        pos_start=self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(Constants.TOK_EQUALS, pos_start=pos_start, pos_end=self.pos), None
        
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos,'Expected \'=\' after \'!\'')

    def gen_equals(self):
        tok_type = Constants.TOK_EQUALS

        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = Constants.TOK_EE

        return Token(tok_type, pos_start, self.pos)

    def gen_less_than(self):
        tok_type = Constants.TOK_LT

        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = Constants.TOK_GTE

        return Token(tok_type, pos_start, self.pos)

    def gen_greater_than(self):
        tok_type = Constants.TOK_GT

        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = Constants.TOK_GTE

        return Token(tok_type, pos_start, self.pos)

    def gen_minus_or_arrow(self):
        tok_type = Constants.TOK_MINUS
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '>':
            self.advance()
            tok_type= Constants.TOK_ARROW
        return Token(tok_type, pos_start = pos_start, pos_end= self.pos)