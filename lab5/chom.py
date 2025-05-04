import itertools


class Chomsky:
    def __init__(self, Vn, Vt, P, S):
        self.Vn = Vn
        self.Vt = Vt
        self.P = P
        self.P_dictionary = {}
        self.S = S
        self.rules = {}

        pairs = self.P.split(", ")
        for pair in pairs:
            a, b = pair.split("->")
            if "|" in b:
                rules = b.split("|")
            else:
                rules = [b]

            rules_with_spaces = [' '.join(rule) for rule in rules]

            if a in self.P_dictionary:
                self.P_dictionary[a].extend(rules_with_spaces)
            else:
                self.P_dictionary[a] = rules_with_spaces

        print("\nInitial production rules:")
        print(self.display_P_dictionary(self.P_dictionary))

    def eliminate_epsilons(self):
        print("\nStep 1: Eliminated ε-productions:")
        nullable = set()

        changed = True
        while changed:
            changed = False
            for left, rights in self.P_dictionary.items():
                for rule in rights:
                    if rule == "ε" or all(symbol in nullable for symbol in rule.split()):
                        if left not in nullable:
                            nullable.add(left)
                            changed = True

        new_P_dict = {}
        for left, rights in self.P_dictionary.items():
            new_rules = set()
            for rule in rights:
                if rule == "ε":
                    continue
                symbols = rule.split()
                positions = [i for i, sym in enumerate(symbols) if sym in nullable]

                all_combinations = []
                for r in range(len(positions) + 1):
                    for combo in itertools.combinations(positions, r):
                        all_combinations.append(combo)

                for combo in all_combinations:
                    new_rule = [symbols[i] for i in range(len(symbols)) if i not in combo]
                    if new_rule:
                        new_rules.add(" ".join(new_rule))
                    elif left == self.S:
                        new_rules.add("ε")

            new_P_dict[left] = list(new_rules)

        self.P_dictionary = new_P_dict
        print(self.display_P_dictionary(self.P_dictionary))

    def eliminate_unit_rules(self):
        print("\nStep 2: Eliminated unit rules:")
        changed = True
        while changed:
            changed = False
            for left in list(self.P_dictionary.keys()):
                rules = list(self.P_dictionary[left])
                new_rules = []

                for rule in rules:
                    if rule.strip() in self.Vn:
                        if rule.strip() in self.P_dictionary:
                            new_rules.extend(self.P_dictionary[rule.strip()])
                            changed = True
                    else:
                        new_rules.append(rule)

                self.P_dictionary[left] = new_rules

        print(self.display_P_dictionary(self.P_dictionary))

    def eliminate_inaccessible_symbols(self):
        print("\nStep 3: Eliminating inaccessible symbols:")
        accessible = set()
        queue = [self.S]

        while queue:
            current = queue.pop(0)
            if current not in accessible:
                accessible.add(current)
                for rule in self.P_dictionary.get(current, []):
                    for symbol in rule.split():
                        if symbol in self.Vn and symbol not in accessible:
                            queue.append(symbol)

        to_remove = [nt for nt in self.Vn if nt not in accessible]

        for nt in to_remove:
            if nt in self.P_dictionary:
                del self.P_dictionary[nt]

        self.Vn = [nt for nt in self.Vn if nt in accessible]
        print(self.display_P_dictionary(self.P_dictionary))

    def eliminate_nonproductive_symbols(self):
        print("\nStep 4: Eliminating non-productive symbols:")
        productive = set()

        # Find initially productive non-terminals (those that produce only terminals)
        for left, rights in self.P_dictionary.items():
            for rule in rights:
                symbols = rule.split()
                if all(symbol in self.Vt for symbol in symbols):
                    productive.add(left)
                    break

        # Find all productive non-terminals
        changed = True
        while changed:
            changed = False
            for left, rights in self.P_dictionary.items():
                if left in productive:
                    continue

                for rule in rights:
                    symbols = rule.split()
                    if all(symbol in self.Vt or symbol in productive for symbol in symbols):
                        productive.add(left)
                        changed = True
                        break

        # Remove non-productive rules and symbols
        new_P_dict = {}
        for left, rights in self.P_dictionary.items():
            if left not in productive:
                continue

            new_rules = []
            for rule in rights:
                symbols = rule.split()
                if all(symbol in self.Vt or symbol in productive for symbol in symbols):
                    new_rules.append(rule)

            if new_rules:
                new_P_dict[left] = new_rules

        self.P_dictionary = new_P_dict
        self.Vn = [nt for nt in self.Vn if nt in productive]
        print(self.display_P_dictionary(self.P_dictionary))

    def convert_to_cnf(self):
        print("\nStep 5: Converting to Chomsky Normal Form:")

        # Step 1: Convert terminal symbols in longer productions
        terminal_to_nonterminal = {}
        new_nonterm_counter = 0

        # Create new rules for terminals
        for terminal in self.Vt:
            new_nonterminal = f"T{new_nonterm_counter}"
            new_nonterm_counter += 1
            terminal_to_nonterminal[terminal] = new_nonterminal
            self.P_dictionary[new_nonterminal] = [terminal]
            self.Vn.append(new_nonterminal)

        # Replace terminals in longer rules
        for left in list(self.P_dictionary.keys()):
            if left.startswith('T'):
                continue

            rules = list(self.P_dictionary[left])
            new_rules = []

            for rule in rules:
                symbols = rule.split()

                # Skip rules that already conform to CNF (single terminal or two non-terminals)
                if len(symbols) == 1 and symbols[0] in self.Vt:
                    new_rules.append(rule)
                    continue

                # Replace terminals with their corresponding non-terminals in multi-symbol rules
                if len(symbols) >= 2:
                    new_symbols = []
                    for symbol in symbols:
                        if symbol in self.Vt:
                            new_symbols.append(terminal_to_nonterminal[symbol])
                        else:
                            new_symbols.append(symbol)
                    new_rules.append(" ".join(new_symbols))
                else:
                    new_rules.append(rule)

            self.P_dictionary[left] = new_rules

        # Step 2: Break rules with more than 2 symbols on the right side
        pair_to_nonterminal = {}

        changed = True
        while changed:
            changed = False
            for left in list(self.P_dictionary.keys()):
                if left.startswith('T'):
                    continue

                rules = list(self.P_dictionary[left])
                new_rules = []

                for rule in rules:
                    symbols = rule.split()

                    if len(symbols) <= 2:
                        new_rules.append(rule)
                    else:
                        # Create a new non-terminal for the first two symbols
                        first_pair = " ".join(symbols[:2])

                        if first_pair not in pair_to_nonterminal:
                            new_nonterminal = f"N{new_nonterm_counter}"
                            new_nonterm_counter += 1
                            pair_to_nonterminal[first_pair] = new_nonterminal
                            self.P_dictionary[new_nonterminal] = [first_pair]
                            self.Vn.append(new_nonterminal)

                        new_rule = pair_to_nonterminal[first_pair]
                        if len(symbols) > 2:
                            new_rule += " " + " ".join(symbols[2:])

                        new_rules.append(new_rule)
                        changed = True

                self.P_dictionary[left] = new_rules

        print(self.display_P_dictionary(self.P_dictionary))

    def chomsky_normal_form(self):
        self.eliminate_epsilons()
        self.eliminate_unit_rules()
        self.eliminate_inaccessible_symbols()
        self.eliminate_nonproductive_symbols()
        self.convert_to_cnf()
        self.rules = self.P_dictionary

    def display_P_dictionary(self, P_dictionary):
        result = []

        for left, rights in P_dictionary.items():
            if rights:
                rhs = '|'.join(rights)
                result.append(f"{left}->{rhs}")

        return ', '.join(result)


if __name__ == "__main__":
    Vn = ["S", "A", "B", "C", "D"]
    Vt = ["a", "b"]
    P = "S->AC|bA|B|aA, A->ε|aS|ABab, B->a|bS, C->abC, D->AB"
    S = "S"

    chomsky = Chomsky(Vn, Vt, P, S)
    chomsky.chomsky_normal_form()