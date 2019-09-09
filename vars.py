game = None
network = None

host_thread = None

screen = None
mixer = None

state = None
substate = None

"""
State List:

hosting_game
    awaiting_join
    awaiting_ready
    awaiting_start

joining_game
    awaiting_connection
    awaiting_ready
    awaiting_start

firing
    awaiting_input
    awaiting_reply

receiving_fire
    None

game_over
    won
    lost
    disconnect
"""