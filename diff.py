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

    @property
    def diff_str(self):
        if self.op == DELETION_OP:
            return self.old_str
        else:
            return self.new_str
        
    @diff_str.setter
    def diff_str(self, s):
        if self.op == DELETION_OP:
            self.old_str = s
        elif self.op == INSERTION_OP:
            self.new_str = s
        else:
            self.old_str = s
            self.new_str = s
        self.len = len(s)
        

    def __iter__(self):
        for each in self.__dict__.values():
            yield each

    def prepend_diff(self, d : "Diff") -> None:
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

    def append_diff(self, d : "Diff") -> None:
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

            works at all levels - character/word/line
        '''
        self.diffs.append(Diff(EQUAL_OP, '', ''))

        del_count, ins_count = 0, 0
        del_text, ins_text = '', ''

        i = 0

        while i < len(self.diffs):
            if self.diffs[i].op == DELETION_OP:
                del_count += 1
                del_text += self.diffs[i].old_str
                i += 1
            elif self.diffs[i].op == INSERTION_OP:
                ins_count += 1
                ins_text += self.diffs[i].new_str
                i += 1
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

                    i -= (ins_count + del_count - 1)

                    if del_count > 0:
                        i += 1
                    if ins_count > 0:
                        i += 1
                elif i > 0 and self.diffs[i-1].op == EQUAL_OP:
                    # merge equality
                    self.diffs[i-1].append_diff(self.diffs[i])
                    del self.diffs[i]
                else:
                    i += 1

                del_count, ins_count = 0, 0
                del_text, ins_text = '', ''

        self.transpose_chaffs()

    def transpose_chaffs(self):
        '''
            A<ins>BA</ins>C -> <ins>AB</ins>AC  
            A<ins>BC</ins>B -> AB<ins>CB</ins>

            return: diff with chaffs and transposed
        '''
        i = 1
        change = False

        while i < len(self.diffs) - 1:
            if self.diffs[i-1].op == EQUAL_OP and self.diffs[i+1].op == EQUAL_OP:
                if self.diffs[i].diff_str.endswith(self.diffs[i-1].diff_str):
                    self.diffs[i].diff_str = self.diffs[i-1].diff_str + self.diffs[i].diff_str[:len(self.diffs[i-1].diff_str)]
                    self.diffs[i+1].diff_str = self.diffs[i-1].diff_str + self.diffs[i+1].diff_str

                    del self.diffs[i-1]
                    change = True
                elif self.diffs[i].diff_str.startswith(self.diffs[i+1].diff_str):
                    self.diffs[i-1].diff_str = self.diffs[i-1].diff_str + self.diffs[i+1].diff_str
                    self.diffs[i].diff_str = self.diffs[i].diff_str[self.diffs[i+1].diff_str:] + self.diffs[i+1].diff_str

                    del self.diffs[i+1]
                    change = True
            i += 1

        if change:
            self.cleanup_merge()

    def cleanup_semantic(self):
        '''
            semantic cleanup of the diff improves human readability

            returns: a semantically cleaned up version of the diff
        '''
        equality_stack = []
        preceding_changes = 0
        succeeding_changes = 0

        changes = False

        i = 0

        while i < len(self.diffs):
            if self.diffs[i].op == EQUAL_OP:
                preceding_changes = succeeding_changes
                equality_stack.append(i)
                succeeding_changes = 0
            else:
                succeeding_changes += self.diffs[i].len
                

                if len(equality_stack) > 0:
                    last_equality = equality_stack[-1]
                    
                    if self.diffs[last_equality].len <= preceding_changes and \
                        self.diffs[last_equality].len <= succeeding_changes:
                        # change chaff to insertion and deletion
                        self.diffs.insert(last_equality, Diff(DELETION_OP, self.diffs[last_equality].diff_str, None))
                        self.diffs[last_equality + 1].update_diff(INSERTION_OP, self.diffs[last_equality + 1].diff_str)

                        # delete the currently processed equality
                        equality_stack.pop()

                        if len(equality_stack) != 0:
                            # pop the previous equality since it needs to be processed
                            # as its context has changed
                            equality_stack.pop()
                        if len(equality_stack):
                            i = equality_stack[-1]
                        else:
                            i = -1
                        preceding_changes, succeeding_changes = 0, 0
                        changes = True

            i += 1

        if changes:
            self.cleanup_semantic()

