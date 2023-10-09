from tabulate import tabulate

class Myers:
    def __init__(self, s1 : str, s2 : str) -> None:
        self.s1, self.s2 = s1, s2
        self.edit_graph_trace = self.shortest_edit()

        self.edit_patches = self.backtrack()

        self.edits = []
        for prev, next in self.edit_patches:
            edit = dict()

            if prev[0] == next[0]:
                edit['type'] = '+'
                edit['newchar'] = self.s2[prev[1]]
            elif prev[1] == next[1]:
                edit['type'] ='-'
                edit['oldchar']  = self.s1[prev[0]]
            else:
                edit['newchar'] = self.s1[prev[0]]
                edit['oldchar'] = self.s2[prev[1]]

            self.edits.append(edit)

        print(tabulate(self.edits, headers={'type': 'op', 'oldchar':  'old', 'newchar': 'new'}))

    def shortest_edit(self):
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
            
    def backtrack(self):
        n1, n2 = len(self.s1), len(self.s2)

        x, y = n1, n2

        patches = []

        for d, v in list(enumerate(self.edit_graph_trace))[::-1]:
            k = x - y

            if k == d:
                prev_k = k - 1
            elif k == -d:
                prev_k = k + 1
            elif v[k-1] < v[k+1]:
                prev_k = k + 1
            else:
                prev_k = k - 1

            prev_x = v[prev_k]
            prev_y = prev_x - prev_k

            while x > prev_x and y > prev_y:
                patches.insert(0, ((x-1, y-1),  (x, y)))
                x, y = x-1, y-1

            if d > 0:
                patches.insert(0, ((prev_x, prev_y), (x, y)))

            x, y = prev_x, prev_y

        return patches

    
if __name__ == "__main__":
    Myers('ABCABBA', 'CBABAC')
