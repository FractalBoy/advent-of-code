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
        self.ore_used = 0

    def add_reaction(self, reaction: Reaction):
        self.reactions.append(reaction)

    def produce(self, product='FUEL', supply=defaultdict(lambda: 0)):
        target_reaction = next(
            filter(lambda r: r.product.chemical == product, self.reactions), None)

        if target_reaction == None:
            raise Exception(f"there's no way to produce {product}!")

        while len(list(incomplete_reactions(target_reaction.reagents, supply))):
            for reagent in incomplete_reactions(target_reaction.reagents, supply):
                if reagent.chemical == 'ORE':
                    supply['ORE'] += reagent.quantity
                    self.ore_used += reagent.quantity
                else:
                    self.produce(product=reagent.chemical, supply=supply)

        for reagent in target_reaction.reagents:
            supply[reagent.chemical] -= reagent.quantity

        supply[target_reaction.product.chemical] += target_reaction.product.quantity 
        return self.ore_used

def incomplete_reactions(reagents, supply):
    return (r for r in reagents if supply[r.chemical] < r.quantity)


if __name__ == '__main__':
    main()
