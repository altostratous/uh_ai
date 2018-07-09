from collections import Counter


class PrioritySet:
    def __init__(self, input_list=None):
        self.set = Counter()
        if input_list is not None:
            self.initiate_from_given_list(input_list)

    def add(self, x):
        self.set[x] += 1

    def pop_most_frequent(self):
        while True:
            try:
                out = self.set.most_common(1)[0][0]
                break
            except IndexError:
                raise Exception("Pop From Empty List")
        self.set.pop(out)
        return out

    def initiate_from_given_list(self, input_list):
        self.set = Counter(input_list)

