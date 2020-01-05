#!/usr/bin/env python

import fileinput
from collections import defaultdict


def main():
    chain_reaction = ChainReaction()

    for line in fileinput.input():
        reagents, product = line.strip().split(' => ')
        quantity, chemical = product.split(' ')
        product = Product(chemical, quantity)
        reaction = Reaction(product)
        reagents = reagents.split(', ')
        for reagent in reagents:
            quantity, chemical = reagent.split(' ')
            reaction.add_reagent(chemical, quantity)

        chain_reaction.add_reaction(reaction)

    print(chain_reaction.produce())


class Chemical():
    def __init__(self, chemical, quantity):
        self.chemical = chemical
        self.quantity = int(quantity)


class Reagent(Chemical):
    pass


class Product(Chemical):
    pass


class Reaction():
    def __init__(self, product):
        self.reagents = []
        self.product = product

    def add_reagent(self, chemical, quantity):
        self.reagents.append(Reagent(chemical, quantity))


class ChainReaction():
    def __init__(self):
        self.reactions = []
        self.supply = defaultdict(lambda: 0)
        self.ore_consumed = 0

    def add_reaction(self, reaction: Reaction):
        self.reactions.append(reaction)

    def produce(self, product='FUEL', quantity=1):
        if product == 'ORE':
            self.supply['ORE'] += quantity
            self.ore_consumed += quantity
            return 

        reaction = next(
            filter(lambda r: r.product.chemical == product, self.reactions), None)

        if reaction == None:
            raise Exception(f"there's no way to produce {product}!")

        while len(list(self.incomplete_reactions(reaction))):
            for reagent in self.incomplete_reactions(reaction):
                self.produce(product=reagent.chemical, quantity=reagent.quantity)

        for reagent in reaction.reagents:
            self.supply[reagent.chemical] -= reagent.quantity

        self.supply[reaction.product.chemical] += reaction.product.quantity
        return self.ore_consumed

    def incomplete_reactions(self, reaction):
        return (r for r in reaction.reagents if self.supply[r.chemical] < r.quantity)


if __name__ == '__main__':
    main()
