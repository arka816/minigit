'''
    implementation of a diff class

    implementation of diffs class
'''

__author__ = 'arka'

from tabulate import tabulate
from constants import EQUAL_OP, DELETION_OP, INSERTION_OP

OPS = {EQUAL_OP, DELETION_OP, INSERTION_OP}

class Diff:
    '''
        implementation of character-level diff
    '''
    def __init__(self, op: str, old_str: str, new_str: str) -> None:
        assert old_str is not None or new_str is not None or (len(old_str) == len(new_str))
        assert op in OPS

        self.op = op
        self.old_str = old_str
        self.new_str = new_str
        if old_str is not None:
            self.len = len(old_str)
        if new_str is not None:
            self.len = len(new_str)

    def __iter__(self):
        for each in self.__dict__.values():
            yield each

    def append_str(self, old_str : str, new_str: str) -> None:
        '''
            adds old and new strings to current strings
        '''
        assert old_str is not None or new_str is not None or (len(old_str) == len(new_str))

        if old_str is not None:
            self.old_str = self.old_str + old_str
        if new_str is not None:
            self.new_str = self.new_str + new_str
        self.len = len(self.old_str)


class Diffs:
    '''
        implementation of list of character-level diffs
    '''
    def __init__(self, diffs : list[Diff]) -> None:
        self.diffs = diffs

    def __repr__(self) -> str:
        return tabulate(self.diffs)

    def merge_char_ops(self):
        '''
            merge adjacent segments of similar character level operations
            to form similar string level operations
        '''
        merged_diffs = []

        for i, diff in enumerate(self.diffs):
            if i == 0:
                curr_diff = diff
            else:
                # check if new op encountered
                if diff.op == curr_diff.op:
                    curr_diff.append_str(diff.old_str, diff.new_str)
                else:
                    merged_diffs.append(curr_diff)
                    curr_diff = diff

        merged_diffs.append(curr_diff)

        self.diffs = merged_diffs
