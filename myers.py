'''
    implementation of Myers diff algorithm
    for character level diff
'''

__author__ = 'Arka'


from diff import Diff, Diffs
from constants import EQUAL_OP, DELETION_OP, INSERTION_OP

class Myers:
    '''
        implementation of Myers diff algorithm at character level

        produces a patch to convert string defined by s1 to string defined by s2 
    '''
    def __init__(self, s1 : str, s2 : str) -> None:
        '''
            @input: s1 - initial text
            @input: s2 - final text
        '''
        self.s1, self.s2 = s1, s2
        self.edit_graph_trace = self.shortest_edit()

        self.edit_patches = self.backtrack()

        self.edits = []
        for prev_pos, next_pos in self.edit_patches:
            if prev_pos[0] == next_pos[0]:
                diff = Diff(INSERTION_OP, None, self.s2[prev_pos[1]])
            elif prev_pos[1] == next_pos[1]:
                diff = Diff(DELETION_OP, self.s1[prev_pos[0]], None)
            else:
                diff = Diff(EQUAL_OP, self.s2[prev_pos[1]], self.s1[prev_pos[0]])

            self.edits.append(diff)

        self.diffs = Diffs(self.edits)

        self.diffs.cleanup()

        print(self.diffs)

    def shortest_edit(self) -> list:
        '''
            constructs the k-v graph

            @returns: list containing all the levels of the graph
        '''
        n1, n2 = len(self.s1), len(self.s2)

        # max depth of the k-v graph (maximum number of edits possible)
        n = n1 + n2

        # k-d graph
        v = [0] * (2 * n + 1)
        v[0] = 0

        # traces of the k-d graph
        v_trace = []

        for d in range(1, n):
            v_trace.append(v.copy())
            for k in range(-d, d+1, 2):
                if k == -d:
                    x = v[k+1]
                elif k == d:
                    x = v[k-1] + 1
                elif v[k-1] < v[k+1]:
                    x = v[k+1]
                else:
                    x = v[k-1] + 1

                y = x-k

                while x < n1 and y < n2 and self.s1[x] == self.s2[y]:
                    x, y = x+1, y+1

                v[k] = x

                if x >= n1 and y >= n2:
                    v_trace.append(v.copy())
                    return v_trace

    def backtrack(self) -> list:
        '''
            backtrack through the edit graph to get a list of patches

            @returns: list of patches
        '''
        n1, n2 = len(self.s1), len(self.s2)

        x, y = n1, n2

        patches = []

        for d, v in list(enumerate(self.edit_graph_trace))[::-1]:
            k = x - y

            if k == d:
                prev_pos_k = k - 1
            elif k == -d:
                prev_pos_k = k + 1
            elif v[k-1] < v[k+1]:
                prev_pos_k = k + 1
            else:
                prev_pos_k = k - 1

            prev_pos_x = v[prev_pos_k]
            prev_pos_y = prev_pos_x - prev_pos_k

            while x > prev_pos_x and y > prev_pos_y:
                patches.insert(0, ((x-1, y-1),  (x, y)))
                x, y = x-1, y-1

            if d > 0:
                patches.insert(0, ((prev_pos_x, prev_pos_y), (x, y)))

            x, y = prev_pos_x, prev_pos_y

        return patches


if __name__ == "__main__":
    text_1 = 'I am the very model of a modern major general.'
    text_2 = '`Twas brillig, and the slithy toves did gyre and gimble in the wabe.'

    text_1 = 'Hovering'
    text_2 = 'My government'

    text_1 = 'It was a dark and stormy night.'
    text_2 = 'The black can in the cupboard.'

    text_1 = '''I am the very model of a modern Major-General,
            I've information vegetable, animal, and mineral,
            I know the kings of England, and I quote the fights historical,
            From Marathon to Waterloo, in order categorical.'''
    text_2 = '''I am the very model of a cartoon individual,
            My animation's comical, unusual, and whimsical,
            I'm quite adept at funny gags, comedic theory I have read,
            From wicked puns and stupid jokes to anvils that drop on your head.'''

    Myers(text_1, text_2)
