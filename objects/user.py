class User:
    """User object with score, objects and network info"""

    def __init__(self, board):
        # Score
        self.score = 0

        # User's board
        self.board = board
