from collections import Counter


class PrioritySet:
    def __init__(self, input_list=None):
        self.set = []
        self.counts = []  # parallel list for number of repetition of objects in set
        if input_list is not None:
            self.initiate_from_given_list(input_list)

    def add(self, x):
        if self.set.__contains__(x):
            self.counts[self.set.index(x)] += 1
            return
        self.set.append(x)
        self.counts.append(1)

    def pop_most_frequent(self):
        out = self.set.pop(self.counts.index(max(self.counts)))
        self.counts.pop(self.counts.index(max(self.counts)))
        return out

    def initiate_from_given_list(self, input_list):
        counter_list = Counter(input_list)
        for x in counter_list:
            self.set.append(x)
            self.counts.append(counter_list[x])

