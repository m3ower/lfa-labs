import random
from enum import Enum


class ChomskyType(Enum):
    TYPE0 = "Type 0 (Unrestricted Grammar)"
    TYPE1 = "Type 1 (Context-Sensitive Grammar)"
    TYPE2 = "Type 2 (Context-Free Grammar)"
    TYPE3 = "Type 3 (Regular Grammar)"


class Grammar:
    def __init__(self):
        self.VN = {'S', 'A', 'B'}
        self.VT = {'a', 'b', 'c'}
        self.P = {
            'S': ['aS', 'bS', 'cA'],
            'A': ['aB'],
            'B': ['aB', 'bB', 'c']
        }
        self.start_symbol = 'S'

    def classify_chomsky(self):
        is_right_regular = all(
            len(prod) <= 2 and (len(prod) == 1 and prod[0] in self.VT or
                                (len(prod) == 2 and prod[0] in self.VT and prod[1] in self.VN))
            for prods in self.P.values()
            for prod in prods
        )

        is_left_regular = all(
            len(prod) <= 2 and (len(prod) == 1 and prod[0] in self.VT or
                                (len(prod) == 2 and prod[0] in self.VN and prod[1] in self.VT))
            for prods in self.P.values()
            for prod in prods
        )

        if is_right_regular or is_left_regular:
            return ChomskyType.TYPE3

        is_context_free = all(
            len(nt) == 1 and nt in self.VN
            for nt in self.P.keys()
        )

        if is_context_free:
            return ChomskyType.TYPE2

        is_context_sensitive = all(
            len(left) <= len(right) for left, rights in self.P.items() for right in rights
        )

        if is_context_sensitive:
            return ChomskyType.TYPE1

        return ChomskyType.TYPE0

    def generate_strings(self, n=5):
        def derive(symbol):
            if symbol in self.VT:
                return symbol
            production = random.choice(self.P[symbol])
            return ''.join(derive(s) for s in production)

        valid_strings = set()
        while len(valid_strings) < n:
            result = derive(self.start_symbol)
            if len(result) <= 15:
                valid_strings.add(result)
        return list(valid_strings)

    def to_finite_automaton(self):
        states = {'q0', 'qf'} | {f'q_{nt}' for nt in self.VN}
        transitions = {state: {} for state in states}

        for nt, prods in self.P.items():
            current = f'q_{nt}'
            for prod in prods:
                next_state = f'q_{prod[1]}' if len(prod) > 1 and prod[1] in self.VN else 'qf'
                transitions[current][prod[0]] = next_state

        for prod in self.P['S']:
            next_state = f'q_{prod[1]}' if len(prod) > 1 and prod[1] in self.VN else 'qf'
            transitions['q0'][prod[0]] = next_state

        return FiniteAutomaton(states, self.VT, transitions, 'q0', {'qf'})


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def check_string(self, input_string):
        current = self.start_state
        for symbol in input_string:
            if symbol not in self.alphabet or \
                    current not in self.transitions or \
                    symbol not in self.transitions[current]:
                return False
            current = self.transitions[current][symbol]
        return current in self.accept_states


def main():
    grammar = Grammar()

    print(f"Grammar Classification: {grammar.classify_chomsky().value}")

    print("Generated strings:")
    for s in grammar.generate_strings(5):
        print(s)

    fa = grammar.to_finite_automaton()
    test_strings = ["cac", "bbaac", "caabaac", "aacbc"]

    print("\nTesting strings:")
    for s in test_strings:
        result = fa.check_string(s)
        print(f"'{s}' is {'valid' if result else 'invalid'}")


if __name__ == "__main__":
    main()