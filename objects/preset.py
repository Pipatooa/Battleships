class Preset:
    """Contains info to create a game"""

    def __init__(self, json):
        self.NAME = json["display"]
        self.BOARD_SIZE = json["size"]
        self.SHIPS = json["ships"]
        self.DESCRIPTION = json["description"]
