class User:
    """User object with score, objects and network info"""

    def __init__(self, board, socket=None):
        # Score
        self.score = 0

        # User's board
        self.board = board

        # User's socket (used to keep track of other player's socket)
        self.socket = socket
