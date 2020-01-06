#!/usr/bin/env python

import fileinput
import random
from collections import defaultdict
from math import ceil, floor


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
    print(chain_reaction.consume_ore(1_000_000_000_000))


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
                num_reactions = ceil(
                    (quantity - self.supply[chemical]) / reaction.product.quantity)
                for reagent in reaction.reagents:
                    new_needed[reagent.chemical] += reagent.quantity * \
                        num_reactions

                self.supply[chemical] += num_reactions * \
                    reaction.product.quantity - quantity

            needed = new_needed

        return self.ore_consumed

    def consume_ore(self, ore):
        self.supply.clear()
        min_fuel, max_fuel = 0, ore

        while min_fuel <= max_fuel:
            estimate = (min_fuel + max_fuel + 1) // 2
            self.ore_consumed = 0
            self.produce(quantity=estimate)
            if self.ore_consumed <= ore:
                min_fuel = estimate
            elif self.ore_consumed > ore:
                max_fuel = estimate - 1
            
            if min_fuel == max_fuel:
                return min_fuel

        if min_fuel == max_fuel + 1:
            return max_fuel

        return False

    def incomplete_reactions(self, reaction):
        return (r for r in reaction.reagents if self.supply[r.chemical] < r.quantity)


if __name__ == '__main__':
    main()
