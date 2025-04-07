# src/modules/inventory.py
class Inventory:
    def __init__(self):
        self.has_sword = False
        self.fragments = 0
        self.supercollateral = 0

    def add_sword(self):
        self.has_sword = True

    def remove_sword(self):
        self.has_sword = False

    def add_fragment(self):
        self.fragments += 1

    def add_supercollateral(self, amount):
        self.supercollateral += amount

    def spend_supercollateral(self, amount):
        if self.supercollateral >= amount:
            self.supercollateral -= amount
            return True
        return False