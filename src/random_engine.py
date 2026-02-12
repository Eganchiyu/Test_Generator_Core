import random

class RandomEngine:
    def __init__(self, seed: int):
        self.seed = seed
        self.rng = random.Random(seed)

    def sample(self, population, k):
        return self.rng.sample(population, k)

    def shuffle(self, population):
        self.rng.shuffle(population)

    def randint(self, a, b):
        return self.rng.randint(a, b)
