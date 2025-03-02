import graphviz

class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def is_deterministic(self):
        for state in self.states:
            for symbol in self.alphabet:
                destinations = self.get_transitions(state, symbol)
                if len(destinations) > 1:
                    return False

        return True

    def get_transitions(self, state, symbol):
        destinations = []
        for (s, sym), dest_states in self.transitions.items():
            if s == state and sym == symbol:
                if isinstance(dest_states, list):
                    destinations.extend(dest_states)
                else:
                    destinations.append(dest_states)
        return destinations

    def to_regular_grammar(self):
        grammar = {}

        for (state, symbol), destinations in self.transitions.items():
            if state not in grammar:
                grammar[state] = []

            dest_list = destinations if isinstance(destinations, list) else [destinations]

            for dest in dest_list:
                if dest in self.final_states:
                    grammar[state].append(f"{symbol}")
                    grammar[state].append(f"{symbol}{dest}")
                else:
                    grammar[state].append(f"{symbol}{dest}")


        if self.start_state in self.final_states:
            if self.start_state not in grammar:
                grammar[self.start_state] = []
            grammar[self.start_state].append("ε")

        return grammar

    def to_dfa(self):
        if self.is_deterministic():
            return self

        dfa_states = []
        dfa_transitions = {}
        dfa_final_states = []

        start_closure = frozenset([self.start_state])
        unprocessed_states = [start_closure]
        dfa_states.append(start_closure)

        while unprocessed_states:
            current_state = unprocessed_states.pop(0)

            for symbol in self.alphabet:
                next_state_set = set()


                for state in current_state:
                    next_states = self.get_transitions(state, symbol)
                    next_state_set.update(next_states)

                if not next_state_set:
                    continue

                next_state = frozenset(next_state_set)

                dfa_transitions[(current_state, symbol)] = next_state

                if next_state not in dfa_states:
                    dfa_states.append(next_state)
                    unprocessed_states.append(next_state)

        for state in dfa_states:
            if any(s in self.final_states for s in state):
                dfa_final_states.append(state)

        state_map = {state: f"q{i}" for i, state in enumerate(dfa_states)}

        new_transitions = {}
        for (state, symbol), next_state in dfa_transitions.items():
            new_transitions[(state_map[state], symbol)] = state_map[next_state]

        return FiniteAutomaton(
            states=[state_map[state] for state in dfa_states],
            alphabet=self.alphabet,
            transitions=new_transitions,
            start_state=state_map[dfa_states[0]],
            final_states=[state_map[state] for state in dfa_final_states]
        )

    def visualize(self):
        dot = graphviz.Digraph(comment='Finite Automaton')

        for state in self.states:
            if state in self.final_states:
                dot.node(state, shape='doublecircle')
            else:
                dot.node(state, shape='circle')

        dot.node('start', style='invisible')
        dot.edge('start', self.start_state)

        for (state, symbol), destinations in self.transitions.items():
            if isinstance(destinations, list):
                for dest in destinations:
                    dot.edge(state, dest, label=symbol)
            else:
                dot.edge(state, destinations, label=symbol)

        return dot



states = ['q0', 'q1', 'q2', 'q3']
alphabet = ['a', 'b', 'c']
transitions = {
    ('q0', 'a'): ['q0', 'q1'],
    ('q1', 'b'): 'q2',
    ('q2', 'a'): 'q2',
    ('q2', 'b'): 'q3',
    ('q2', 'c'): 'q0'
}
start_state = 'q0'
final_states = ['q3']

fa = FiniteAutomaton(states, alphabet, transitions, start_state, final_states)

grammar = fa.to_regular_grammar()
print("Regular Grammar:")
for non_terminal, productions in grammar.items():
    for production in productions:
        print(f"{non_terminal} → {production}")

is_dfa = fa.is_deterministic()
print(f"\nIs the FA deterministic? {'Yes' if is_dfa else 'No'}")
print("Because the state 'q0' and input 'a' can lead to multiple states: q0 and q1")

if not is_dfa:
    print("\nConverting NDFA to DFA...")
    dfa = fa.to_dfa()
    print("DFA states:", dfa.states)
    print("DFA transitions:")
    for (state, symbol), dest in dfa.transitions.items():
        print(f"δ({state}, {symbol}) = {dest}")
    print("DFA final states:", dfa.final_states)

fa_visual = fa.visualize()
fa_visual.render('fa', format='png', cleanup=True)

if not is_dfa:
    dfa_visual = dfa.visualize()
    dfa_visual.render('dfa', format='png', cleanup=True)