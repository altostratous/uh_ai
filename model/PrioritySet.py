from collections import Counter


class PrioritySet(Counter):
    @classmethod
    def fromkeys(cls, iterable, v=None):
        pass

    def __init__(self, input_list=None):
        super().__init__(input_list)

    def add(self, x):
        self[x] += 1

    def pop_most_frequent(self):
        while True:
            try:
                out = self.most_common(1)[0][0]
                break
            except IndexError:
                raise Exception("Pop From Empty List")
        self.pop(out)
        return out
