# src/modules/checkpoint.py
class CheckpointSystem:
    def __init__(self):
        self.last_checkpoint = None

    def save(self, player):
        self.last_checkpoint = {
            "x": player.rect.x,
            "y": player.rect.y,
            "infection_level": player.infection_level,
            "hp": player.hp,
            "has_sword": player.inventory.has_sword,
            "fragments": player.inventory.fragments,
            "supercollateral": player.inventory.supercollateral
        }

    def load(self, player):
        if self.last_checkpoint:
            player.rect.x = self.last_checkpoint["x"]
            player.rect.y = self.last_checkpoint["y"]
            player.infection_level = self.last_checkpoint["infection_level"]
            player.hp = self.last_checkpoint["hp"]
            player.inventory.has_sword = self.last_checkpoint["has_sword"]
            player.inventory.fragments = self.last_checkpoint["fragments"]
            player.inventory.supercollateral = self.last_checkpoint["supercollateral"]

    def has_checkpoint(self):
        return self.last_checkpoint is not None