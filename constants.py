import string
class Constants:
    TOK_INT='INT'
    TOK_FLOAT='FLOAT'
    TOK_PLUS='PLUS'
    TOK_MINUS='MINUS'
    TOK_MULTIPLY='MULTIPLY'
    TOK_DIVIDE='DIVIDE'
    TOK_LPAREN='LPAREN'
    TOK_RPAREN='RPAREN'
    TOK_EOF='EOF'

    DIGITS = '0123456789'
    LETTERS=string.ascii_letters

    TOK_POW='POW'
    
    TOK_IDENTIFIER='IDENTIFIER'
    TOK_KEYWORD='KEYWORD'
    TOK_EQUALS='EQUALS'

    LIST_KEYWORDS = [
        'var',
    ]
