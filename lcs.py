'''
    longest common subsequence algorithm
    for line level diff

    original work by D.S. Hirschberg, Princeton University
    see paper: https://dl.acm.org/doi/pdf/10.1145/360825.360861
'''

from diff import Diffs, Diff
from constants import EQUAL_OP, DELETION_OP, INSERTION_OP

class LCS:
    '''
        implementation of LCS class for calculating line level diffs

        finds longest common subsequences of lines through naive approach
        modified lines in between common subsequences are reported as insertion / deletion pairs
    '''
    def __init__(self, s1: str, s2: str) -> None:
        '''
            @params: s1 - initial text
            @params: s2 - final text
        '''
        self.l1 = [line.strip('\r') for line in s1.split('\n')]
        self.l2 = [line.strip('\r') for line in s2.split('\n')]

        # print(self.l1)
        # print(self.l2)

    def compute_lcs_size(self, l1: list[str], l2: list[str]) -> list:
        '''
            implements naive exact LCS solution
            time complexity:  O(len(s1) * len(s2))
            space complexity: O(len(s1))

            @returns: L[n1, :]
        '''
        n1, n2 = len(l1), len(l2)

        prev = [0] * (n2 + 1)
        curr = [0] * (n2 + 1)

        for i in range(1, n1 + 1):
            for j in range(1, n2 + 1):
                if l1[i - 1] == l2[j - 1]:
                    curr[j] = 1 + prev[j - 1]
                else:
                    curr[j] = max(curr[j - 1], prev[j])

            prev = curr.copy()

        return curr[1:]
    
    def compute_lcs(self, l1: list[str], l2: list[str], n1: int, n2: int, \
                    p1: int = 0, p2: int = 0) -> list[tuple]:
        '''
            recursively enumerates the actual longest common subsequence
            from the lcs size algorithm

            @returns: list of matches as tuples
        '''
        # Handle edge cases
        if n2 == 0:
            return []
        elif n1 == 1:
            for j in range(n2):
                if l1[0] == l2[j]:
                    return [(p1, p2 + j)]
            return []
        else:
            # Evaluate L[i, j] and L*[i, j] for j = 0,...,n2
            i = n1 // 2

            L = self.compute_lcs_size(l1[:i], l2)
            L_c = self.compute_lcs_size(l1[-1:i - 1:-1], l2[::-1])

            k, M = 0, 0

            for j in range(n2):
                if L[j] + L_c[n2 - j - 1] > M:
                    M = L[j] + L_c[n2 - j - 1]
                    k = j

            C1 = self.compute_lcs(l1[:i], l2[:k + 1], i, k + 1, p1 + 0, p2 + 0)
            C2 = self.compute_lcs(l1[i:], l2[k + 1:], n1 - i, n2 - k - 1, p1 + i, p2 + k + 1)
            
            return C1 + C2

    
    def to_diff(self) -> Diffs:
        '''
            converts inter-match sequences to subsequent insertions and deletions
        '''
        lcs = self.compute_lcs(self.l1, self.l2, len(self.l1), len(self.l2))

        # fill in inter-LCS contiguous unmatched sequences using insertions and deletions
        last_i, last_j = -1, -1

        self.diffs = []

        lcs.append((len(self.l1), len(self.l2)))

        for i, j in lcs:
            del_count = i - last_i - 1
            ins_count = j - last_j - 1

            if del_count > 0:
                self.diffs.extend([Diff(DELETION_OP, old_str, None) for old_str in self.l1[last_i + 1: i]])
            if ins_count > 0:
                self.diffs.extend([Diff(INSERTION_OP, None, new_str) for new_str in self.l2[last_j + 1: j]])
            
            if i < len(self.l1) and j < len(self.l2):
                self.diffs.append(Diff(EQUAL_OP, self.l1[i], self.l2[j]))

            last_i, last_j = i, j

        self.diffs = Diffs(self.diffs)

        return self.diffs



if __name__ == '__main__':
    text_1 = open("./test/file_1.txt").read()
    text_2 = open("./test/file_2.txt").read()

    lcs = LCS(text_1, text_2)
    diff = lcs.to_diff()

    print(diff)
