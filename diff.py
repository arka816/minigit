'''
    implementation of a diff class

    implementation of diffs class
'''

__author__ = 'arka'

class Diff:
    '''
        implementation of character-level diff
    '''
    def __init__(self, op: str, old_str: str, new_str: str) -> None:
        self.op = op
        self.old_str = old_str
        self.new_str = new_str

class Diffs:
    '''
        implementation of list of character-level diffs
    '''
    def __init__(self, diffs : list[Diff]) -> None:
        self.diffs = diffs

    def merge(self):
        '''
            merge adjacent segments of similar operations
        '''
        pass
