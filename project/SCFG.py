from copy import deepcopy
from typing import Dict, Set, Tuple

import tkinter as tk
import random


START = 'S'

SHAPE_DIM = 100
WINDOW_DIM = 6 * 100


class SCFG:
    tk_shapes = []
    tk_images = []

    frequencies: Dict[str, Dict[Tuple[str | None, str, Tuple[str] | None], int]] = {}
    n_state: int = 0

    def __init__(self):
        self.non_terminals: Set[str] = set()
        self.terminals: Set[str] = set()
        self.productions: Dict[str, Set[Tuple[str | None, str, Tuple[str] | None]]] = {}
        self.start: str = START
        self.probabilities: Dict[str, float] = {}

    # rule parts named as follows: u -> v
    def parse_least_general_conforming(self, *examples: Dict):
        # BFS down the “scene graph”
        for example in examples:
            queue = [(example, None, 'S')]

            while queue:
                shape, direction, parent = queue[0]
                queue = queue[1:]

                terminal = shape['ID'] + '.png'
                if 'children' in shape:
                    new_states = []
                    for _ in shape['children']:
                        new_states.append(str(self.n_state))
                        self.n_state += 1
                    new_states = tuple(new_states)
                else:
                    new_states = None

                u = parent
                v = (direction, terminal, new_states)

                self.terminals.add(terminal)
                if new_states:    # not None
                    for non_terminal in new_states:
                        self.non_terminals.add(non_terminal)

                if u not in self.productions:
                    self.productions[u] = set()
                if v not in self.productions[u]:
                    self.productions[u].add(v)

                if u not in self.frequencies:
                    self.frequencies[u] = {}

                if v not in self.frequencies[u]:
                    self.frequencies[u][v] = 1
                else:
                    self.frequencies[u][v] += 1

                if 'children' in shape:
                    for direction, new_state in zip(shape['children'], new_states):
                        child = shape['children'][direction]
                        queue.append((child, direction, new_state))

        # calculate probabilities from the self.frequencies
        for u in self.frequencies:
            all_outcomes = sum(self.frequencies[u][v] for v in self.frequencies[u])

            for v in self.frequencies[u]:
                direction, shape, children_states = str(v[0]), v[1], ':'.join(v[2]) if v[2] is not None else str(None)
                v_str = str(tuple([direction, shape, children_states]))
                production = u + ' -> ' + v_str

                frequency = self.frequencies[u][v]
                probability = frequency / all_outcomes

                self.probabilities |= {production: probability}

    # rule parts named as follows: u -> v
    def mix_up_tops(self):
        for u in self.productions:
            for v in deepcopy(self.productions[u]):
                match v[1]:
                    case 'spire.png':
                        self.productions[u].add(('up', 'flag.png', None))
                    case 'flag.png':
                        self.productions[u].add(('up', 'spire.png', None))

            for v in self.productions[u]:
                direction, shape, children_states = str(v[0]), v[1], ':'.join(v[2]) if v[2] is not None else str(None)
                v_str = str(tuple([direction, shape, children_states]))
                production = u + ' -> ' + v_str

                self.probabilities[production] = 0.5

    def draw_random_production(self):
        states = ['S']
        coordinates = [(0, 0)]

        self.tk_shapes = []
        self.tk_images = []
        canvas = tk.Canvas(height=WINDOW_DIM, width=WINDOW_DIM, bg="white")

        while states:
            current_state = states[0]
            current_coordinates = coordinates[0]

            states = states[1:]
            coordinates = coordinates[1:]

            ordered_productions = list(self.productions[current_state])

            probabilities = []
            for v in ordered_productions:
                direction, shape, children_states = str(v[0]), v[1], ':'.join(v[2]) if v[2] is not None else str(None)
                v_str = str(tuple([direction, shape, children_states]))
                production = current_state + ' -> ' + v_str
                probabilities.append(self.probabilities[production])

            choice = random.choices(ordered_productions, weights=probabilities, k=1)[0]

            direction, shape = choice[0], choice[1]
            x, y = current_coordinates
            match direction:
                case 'right':
                    x += 1
                case 'up':
                    y += 1

            shape = tk.PhotoImage(file='resources/{}'.format(shape))
            self.tk_shapes.append(shape)
            image = canvas.create_image(x * SHAPE_DIM, (WINDOW_DIM - y * SHAPE_DIM), image=shape, anchor=tk.SW)
            self.tk_images.append(image)

            next_states = choice[2]
            if next_states is not None:
                for next_state in next_states:
                    states.append(next_state)
                    coordinates.append((x, y))

        canvas.pack()
        tk.mainloop()
