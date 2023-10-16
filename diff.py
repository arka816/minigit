'''
    implementation of a diff class

    implementation of diffs class
'''

__author__ = 'arka'

from tabulate import tabulate
from constants import EQUAL_OP, DELETION_OP, INSERTION_OP
from utils import common_prefix, common_suffix

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

    def prepend_diff(self, d : Diff) -> None:
        '''
            prepends new diff to beginning of self
        '''
        assert self.op == d.op

        if self.op == DELETION_OP:
            self.old_str = d.old_str + self.old_str
            self.len += len(d.old_str)
        elif self.op == INSERTION_OP:
            self.new_str = d.new_str + self.new_str
            self.len += len(d.new_str)
        elif self.op == EQUAL_OP:
            self.old_str = d.old_str + self.old_str
            self.new_str = d.new_str + self.new_str
            self.len += len(d.old_str)

    def append_diff(self, d : Diff) -> None:
        '''
            appends new diff to end of self
        '''
        assert self.op == d.op

        if self.op == DELETION_OP:
            self.old_str += d.old_str
            self.len += len(d.old_str)
        elif self.op == INSERTION_OP:
            self.new_str += d.new_str
            self.len += len(d.new_str)
        elif self.op == EQUAL_OP:
            self.old_str += d.old_str
            self.new_str += d.new_str
            self.len += len(d.old_str)

    def update_diff(self, op : str, s : str) -> None:
        self.op = op
        if self.op == DELETION_OP:
            self.old_str = s
        elif self.op == INSERTION_OP:
            self.new_str = s
        else:
            self.old_str = s
            self.new_str = s


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
                    curr_diff.append_diff(diff)
                else:
                    merged_diffs.append(curr_diff)
                    curr_diff = diff

        merged_diffs.append(curr_diff)

        self.diffs = merged_diffs

    def cleanup_merge(self) -> None:
        '''
            reorder and merge like edit sections
        '''
        self.diffs.append(Diff(EQUAL_OP, '', ''))

        del_count, ins_count = 0, 0
        del_text, ins_text = '', ''

        i = 0

        while i < len(self.diffs):
            if self.diffs[i].op == DELETION_OP:
                del_count += self.diffs[i].len
                del_text += self.diffs[i].old_str
            elif self.diffs[i].op == INSERTION_OP:
                ins_count += self.diffs[i].len
                ins_text += self.diffs[i].new_str
            else:
                # handle out past discrepancies
                if ins_count > 0 or del_count > 0:
                    if ins_count > 0 and del_count > 0:
                        # factor out common prefixes
                        l = common_prefix(ins_text, del_text)
                        if l > 0:
                            x = i - del_count - ins_count - 1
                            if x >= 0 and self.diffs[x].op == EQUAL_OP:
                                self.diffs[x].update_diff(EQUAL_OP,  ins_text[:l])
                            else:
                                self.diffs.insert(0, Diff(EQUAL_OP, del_text[:l], ins_text[:l]))
                            ins_text = ins_text[l:]
                            del_text = del_text[l:]

                        # factor out common suffixes
                        l = common_suffix(ins_text, del_text)
                        if l > 0:
                            self.diffs[i].prepend_diff(Diff(EQUAL_OP, del_text[-l:], ins_text[-l:]))
                            ins_text = ins_text[:-l]
                            del_text = del_text[:-l]

                    if ins_count == 0:
                        self.diffs[i - del_count:i] = [Diff(DELETION_OP, del_text, None)]
                    elif del_count == 0:
                        self.diffs[i - ins_count:i] = [Diff(INSERTION_OP, None, ins_text)]
                    else:
                        self.diffs[i - del_count - ins_count:i] = [
                            Diff(DELETION_OP, del_text, None),
                            Diff(INSERTION_OP, None, ins_text)
                        ]

                    i -= (ins_count +  del_count - 1)

                    # TODO: findout why this
                    if del_count > 0:
                        i += 1
                    if ins_count > 0:
                        i += 1
                elif i > 0 and self.diffs[i-1].op == EQUAL_OP:
                    # merge equality
                    self.diffs[i-1].append_diff(self.diffs[i])
                    del diffs[i]
                else:
                    i += 1

                del_count, ins_count = 0, 0
                del_text, ins_text = '', ''
