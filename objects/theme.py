class Theme:
    """Contains color information for drawing objects to the current display

    Used by draw functions"""

    def __init__(self, **kwargs):
        self.BACKGROUND_COLOR = tuple(kwargs["background_color"])
        self.CENTER_COLOR = tuple(kwargs["center_color"])

        self.BOX_COLOR = tuple(kwargs["box_color"])
        self.BOX_OUTLINE_COLOR = tuple(kwargs["box_outline_color"])

        self.BUTTON_COLOR = tuple(kwargs["button_color"])

        self.FONT = kwargs["font"]
        self.TEXT_COLOR = tuple(kwargs["text_color"])

        self.CELL_COLOR = tuple(kwargs["cell_color"])
        self.MISS_COLOR = tuple(kwargs["miss_color"])
        self.HIT_COLOR = tuple(kwargs["hit_color"])

        self.ATTACK_COLOR = tuple(kwargs["attack_color"])
        self.ATTACK_OUTLINE_COLOR = tuple(kwargs["attack_outline_color"])

        self.GRID_COLOR = tuple(kwargs["grid_color"])

        self.SHIP_COLOR = tuple(kwargs["ship_color"])
        self.SUNK_SHIP_COLOR = tuple(kwargs["sunk_ship_color"])
