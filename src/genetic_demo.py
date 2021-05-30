"""genetic_demo.py
author: garrick

Demonstration program of combining genetic algorithms with human input to 
produce music.

# TODO: add colors
"""
from collections import defaultdict
from genetic import genetic_algorithm_step, music_dynamics
from function import UniformRandomFunc, UserPreferenceFunc
from pythonosc import udp_client

import numpy as np

# from synthesis import *  # Potential decomposition of sound-producing functions here

POPULATION_SIZE = 20
AUDIO_SERVER_IP = "127.0.0.1"
AUDIO_SERVER_PORT = 57120

# TODO: move to a util file
def chromosome_to_osc(c: np.ndarray):
    return c.tolist()


class Handler:
    def __init__(self) -> None:
        pass

    def __call__(self) -> None:
        self.eval()

    def eval(self) -> None:
        raise NotImplementedError("Subclasses must override this method")

    def helptext(self) -> str:
        """Allow a form of introspection on the handler, i.e. describing what it 
        does. Used for generating helptext.
        """
        raise NotImplementedError("Subclasses must override this method")


class HandleQuit(Handler):
    def eval(self) -> None:
        global quit  # To modify, must mark global
        quit = True
        print("Goodbye!")

    def helptext(self) -> str:
        return "Quits the program."


class HandleRecord(Handler):
    def eval(self) -> None:
        print("Not implemented!")  # TODO: implement

    def helptext(self) -> str:
        return "Toggles recording."


class HandleLike(Handler):
    def eval(self) -> None:
        if cur_chromosome is None:
            print("No current Chromosome. Use 'next' to play one!")
        print("Not implemented!")  # TODO: implement

    def helptext(self) -> str:
        return "Like the currently playing Chromosome."


class HandleDislike(Handler):
    def eval(self) -> None:
        if cur_chromosome is None:
            print("No current Chromosome. Use 'next' to play one!")
        print("Not implemented!")  # TODO: implement

    def helptext(self) -> str:
        return "Dislike the currently playing Chromosome."


class HandleAdvance(Handler):
    def eval(self) -> None:
        global iter, cur_population, cur_chromosome_idx
        assert iter is not None

        # TODO: learn surrogate function based on current user input

        cur_population, _, _ = genetic_algorithm_step(
            cur_population, f, dynamics=dynamics, pop_size=POPULATION_SIZE,
        )
        iter += 1

        print(f"Generation {iter + 1}")

        cur_chromosome_idx = None

    def helptext(self) -> str:
        return "Advance a generation."


class HandlePush(Handler):
    def eval(self) -> None:
        if cur_chromosome is None:
            print("No current Chromosome. Use 'next' to play one!")
        print("Not implemented!")  # TODO: implement

    def helptext(self) -> str:
        return "Commit the currently playing Chromosome and start a new Part."


class HandlePop(Handler):
    def eval(self) -> None:
        if cur_chromosome is None:
            print("No current Chromosome. Use 'next' to play one!")
        print("Not implemented!")  # TODO: implement

    def helptext(self) -> str:
        return "Remove the most recently added Chromosome."


class HandleNext(Handler):
    def eval(self) -> None:
        global cur_chromosome, cur_chromosome_idx

        if cur_population is None:
            raise RuntimeError("Population not initialized!")

        n = len(cur_population)

        if cur_chromosome_idx is None or cur_chromosome_idx == n - 1:
            cur_chromosome_idx = 0
        else:
            cur_chromosome_idx += 1

        cur_chromosome = cur_population[cur_chromosome_idx]

        print(f"Playing Chromosome {cur_chromosome_idx + 1}/{n}")
        print(cur_chromosome)  # TODO: remove debug line/replace with something prettier

        args = chromosome_to_osc(cur_chromosome)
        client.send_message("/playInstrument", args)

    def helptext(self) -> str:
        return "Play the next Chromosome in the current population."


class HandleClear(Handler):
    def eval(self) -> None:
        print("Not implemented!")  # TODO: implement

    def helptext(self) -> str:
        return "Clear all playing Parts."


def indent_by(s, n):
    return " " * n + s


def handle_help():
    print("List of available commands:")
    handler_to_cmd_strings = defaultdict(list)
    for cmd_string, handler in command_handlers.items():
        handler_to_cmd_strings[handler].append(cmd_string)

    for key in handler_to_cmd_strings.values():
        if key[0] in ["h", "help"]:
            print(indent_by(f"['h', 'help']\t Display helptext.", 2))
            continue

        cmd_strings = f"{key}"
        if len(cmd_strings) < 14:
            print(indent_by(f"{key}\t {command_handlers[key[0]].helptext()}", 2))
        else:
            # Print on two lines
            print(indent_by(f"{key}", 2))
            print(indent_by(f"{command_handlers[key[0]].helptext()}", 4))


handle_quit = HandleQuit()
handle_record = HandleRecord()
handle_advance = HandleAdvance()
handle_like = HandleLike()
handle_dislike = HandleDislike()
handle_push = HandlePush()
handle_pop = HandlePop()
handle_clear = HandleClear()
handle_next = HandleNext()
# XXX: Can add solo (to toggle focus on current part), mute

# NOTE can include shortcuts
command_handlers = {
    "-": handle_dislike,
    "": handle_next,
    "+": handle_like,
    "a": handle_advance,
    "adv": handle_advance,
    "clr": handle_clear,
    "d": handle_dislike,
    "dis": handle_dislike,
    "h": handle_help,
    "help": handle_help,
    "l": handle_like,
    "like": handle_like,
    "n": handle_next,
    "next": handle_next,
    "p": handle_push,
    "pop": handle_pop,
    "push": handle_push,
    "q": handle_quit,
    "quit": handle_quit,
    "r": handle_record,
    "rec": handle_record,
}

quit = False
cur_population = None
cur_chromosome_idx = None
cur_chromosome = None
f = None
dynamics = music_dynamics
iter = None
client = None


def initialize_demo_state(
    ip=AUDIO_SERVER_IP, port=AUDIO_SERVER_PORT, pop_size=POPULATION_SIZE
):
    """Begins genetic algorithm, connects to OSC server for producing sound"""
    global client, cur_population, f, iter

    print("Initializing audio client...")
    client = udp_client.SimpleUDPClient(ip, port)
    print(f"Sending OSC messages to {ip}, port {port}")

    print("Initializing Chromosomes...")
    init_chromosome = dynamics.init
    iter = 0
    cur_population = np.array([init_chromosome() for _ in range(pop_size)])
    f = UniformRandomFunc()

    print(f"Generation {iter + 1}")


def get_input():
    while True:
        inp = input("> ").lower()

        if inp in command_handlers:
            return inp
        else:
            print("Invalid input. Try again ('help' for help).")


# read-eval-print loop
def repl():
    initialize_demo_state()

    print("Enter commands ('help' for help):")
    while not quit:
        cmd = get_input()
        handler = command_handlers[cmd]
        handler()


if __name__ == "__main__":
    repl()
