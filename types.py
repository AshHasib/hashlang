
from errors import RTError

class Value:
    def __init__(self, value):
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