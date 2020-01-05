#!/usr/bin/env python

import fileinput
import random
from collections import defaultdict
from math import ceil


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
        self.reactions = {}
        self.supply = defaultdict(lambda: 0)
        self.ore_consumed = 0

    def add_reaction(self, reaction: Reaction):
        self.reactions[reaction.product.chemical] = reaction

    def produce(self, product='FUEL', quantity=1):
        needed = defaultdict(lambda: 0)
        needed[product] = quantity

        while len(needed):
            new_needed = defaultdict(lambda: 0)

            for chemical, quantity in needed.items():
                if chemical == 'ORE':
                    self.ore_consumed += quantity
                    continue

                reaction = self.reactions[chemical]
                num_reactions = ceil((quantity - self.supply[chemical]) / reaction.product.quantity)
                for reagent in reaction.reagents:
                    new_needed[reagent.chemical] += reagent.quantity * num_reactions

                self.supply[chemical] += num_reactions * reaction.product.quantity - quantity
            
            needed = new_needed

        return self.ore_consumed

    def consume_ore(self, ore):
        fuel_min, fuel_max = 1, 1000

        while fuel_min <= fuel_max:
            fuel_guess = fuel_max + fuel_min // 2
            self.ore_consumed = 0

            for _ in range(0, fuel_guess):
                self.produce()

            if self.ore_consumed > ore:
                fuel_max = fuel_guess + 1
            elif self.ore_consumed < ore:
                fuel_min = fuel_guess - 1
            else:
                return fuel_guess

        return False

    def incomplete_reactions(self, reaction):
        return (r for r in reaction.reagents if self.supply[r.chemical] < r.quantity)


if __name__ == '__main__':
    main()
