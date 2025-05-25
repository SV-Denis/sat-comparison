import timeit
import tracemalloc
import random
from tabulate import tabulate
# ======================== Shared Utilities ========================
def simplify_clauses(clauses, var, val):
    return [c - {var, -var} for c in clauses
            if not ((var in c and val) or (-var in c and not val))]


def find_pure_literals(clauses, assigned=None):
    assigned = assigned or {}
    literals = {lit for c in clauses for lit in c if abs(lit) not in assigned}
    return {abs(lit): lit > 0 for lit in literals if -lit not in literals}

def choose_variable(clauses, assigned):
    unassigned = {abs(lit) for c in clauses for lit in c} - set(assigned)
    return max(unassigned, key=lambda x: sum(x in c or -x in c for c in clauses), default=None)

def unrelevant_clauses(new_clause, clauses, seen):
    for clause in clauses:
        if clause.issubset(new_clause):
            return True
    for clause in clauses:
        if clause.issubset(seen):
            return True
    return False

def resolve(c1, c2):
    resolvents = []
    for lit in c1:
        if -lit in c2:
            new_clause = (c1 | c2) - {lit, -lit}
            if not any(-l in new_clause for l in new_clause):
                resolvents.append(new_clause)
    return resolvents

# ======================== Resolution Solver ========================
def resolution_solver(clauses, max_clauses=10000, max_steps=100000):
    seen = {frozenset(c) for c in clauses}
    clauses = [frozenset(c) for c in clauses]
    steps = 0
    while steps < max_steps:
        new = []
        for i, c1 in enumerate(clauses):
            for c2 in clauses[i + 1:]:
                resolvents = resolve(c1, c2)
                for resolvent in resolvents:
                    steps += 1
                    if not resolvent:
                        return "RES", False
                    fr = frozenset(resolvent)
                    if fr not in seen and not unrelevant_clauses(fr, clauses, seen):
                        if len(seen) >= max_clauses:
                            return "RES", "UNKNOWN"
                        seen.add(fr)
                        new.append(resolvent)
        if not new:
            return "RES", True
        clauses.extend(map(frozenset, new))
    return "RES", "UNKNOWN (max steps reached)"

# ======================== Davis-Putnam ========================

def davis_putnam(clauses, max_clauses=10000):
    clauses = [frozenset(c) for c in clauses]
    assignments = {}
    seen = set(clauses)

    while True:
        # Unit propagation
        while (units := [c for c in clauses if len(c) == 1]):
            var = abs(next(iter(units[0])))
            val = next(iter(units[0])) > 0
            assignments[var] = val
            clauses = simplify_clauses(clauses, var, val)
            seen = {frozenset(c) for c in clauses}  # Update seen

        # Pure literal elimination
        for var, val in find_pure_literals(clauses).items():
            assignments[var] = val
            clauses = simplify_clauses(clauses, var, val)
            seen = {frozenset(c) for c in clauses}  # Update seen

        # Termination checks
        if not clauses:
            return "DP", True, assignments
        if any(not c for c in clauses):
            return "DP", False, None

            # Variable elimination
        var = max({abs(lit) for c in clauses for lit in c},
            key=lambda x: sum(x in c or -x in c for c in clauses), default=None)
        if not var: continue

        pos = [c for c in clauses if var in c]
        neg = [c for c in clauses if -var in c]

        new_clauses = []
        for c1 in pos:
            for c2 in neg:
                for resolvent in resolve(c1, c2):
                    if not resolvent:
                        return "DP", False, None
                    fr = frozenset(resolvent)
                    if fr not in seen and not unrelevant_clauses(fr, clauses, seen):
                        if len(seen) >= max_clauses :
                            return "DP", "UNKNOWN", None
                        seen.add(fr)
                        new_clauses.append(resolvent)

        clauses = [c for c in clauses if var not in c and -var not in c] + new_clauses

# ======================== DPLL Solver ========================
def dpll(clauses, assignments=None):
    assignments = assignments or {}
    clauses = [frozenset(c) for c in clauses]

    # --- Unit Propagation ---
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            if len(clause) == 1:
                lit = next(iter(clause))
                var = abs(lit)
                if var not in assignments:
                    assignments[var] = (lit > 0)
                    changed = True
                    clauses = [frozenset(c - {var, -var}) for c in clauses
                               if not ((var in c and assignments[var]) or
                                       (-var in c and not assignments[var]))]

    # --- Check Termination ---
    if any(len(c) == 0 for c in clauses):
        return None  # UNSAT
    if not clauses:
        return assignments  # SAT

    # --- Pure Literal Elimination ---
    pure_vars = find_pure_literals(clauses, assignments)
    for var, val in pure_vars.items():
        assignments[var] = val
        clauses = [frozenset(c - {var, -var}) for c in clauses
                   if not ((var in c and val) or (-var in c and not val))]

    # --- Splitting Rule ---
    var = choose_variable(clauses, assignments)
    for val in [True, False]:
        new_clauses = [frozenset(c - {var, -var}) for c in clauses
                       if not ((var in c and val) or (-var in c and not val))]
        result = dpll(new_clauses, {**assignments, var: val})
        if result is not None:
            return result
    return None  # UNSAT

# ======================== Testing Framework ========================
def generate_satisfiable_3sat(n_vars, n_clauses):
    variables = list(range(1, n_vars + 1))

    # Create a random satisfiable assignment
    assignment = {var: random.choice([True, False]) for var in variables}

    clauses = []
    for _ in range(n_clauses):
        # Start with a clause that's satisfied by our assignment
        while True:
            clause = set()
            # Pick 3 distinct variables
            for var in random.sample(variables, min(3, len(variables))):
                # Flip the sign with some probability to make it non-trivial
                if random.random() < 0.3:
                    clause.add(-var if assignment[var] else var)
                else:
                    clause.add(var if assignment[var] else -var)

            # Ensure the clause is not tautological and has exactly 3 literals
            if len(clause) == 3 and not any(-lit in clause for lit in clause):
                clauses.append(clause)
                break
    return clauses
def generate_random_3sat(name, n_vars, n_clauses):
    variables = list(range(1, n_vars + 1))
    clauses = []
    for _ in range(n_clauses):
        clause = set()
        while len(clause) < 3:
            var = random.choice(variables)
            sign = random.choice([-1, 1])
            clause.add(var * sign)
        clauses.append(clause)
    return (name, clauses)

def test_cnf(cnf):
    result = dpll([frozenset(c) for c in cnf])
    return "DPLL", "SAT" if result else "UNSAT"


def measure_performance(alg_name, cnf, runs=50):
    def runner():
        if alg_name == "DPLL":
            return test_cnf(cnf)
        elif alg_name == "DP":
            return davis_putnam(cnf)
        elif alg_name == "RES":
            return resolution_solver(cnf)

    time_taken = timeit.timeit(runner, number=runs) / runs

    tracemalloc.start()
    runner()
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    return {
        'time': time_taken,
        'peak_kb': peak / 1024
    }

def generate_3sat_tests(x,y,z,step,Test):
    y += 1
    if Test == "y" or Test == "Y":
        for i in range(z,y,step):
            tests.append((f"3-sat:{i}",generate_satisfiable_3sat(x, i)))
            test_input.append((x,i))
    else:
        for i in range(z,y,step):
            tests.append((f"3-sat:{i}",generate_satisfiable_3sat(i, x)))
            test_input.append((i, x))

if __name__ == "__main__":
    benchmark_results = []
    tests = []
    test_input = []
    print("enter Clause range mode? y/n")
    TEST = input()
    if TEST == "y" or TEST == "Y":
        print("Enter the amount of variables for the generation of 3-SAT problems (the number needs to be 3 or above otherwise it wont work):")
        X = int(input())
        print("Enter the minimum number of clauses for the generation of 3-SAT problems (enter above 0):")
        Z = int(input())
        print("Enter the maximum number of clauses for the generation of 3-SAT problems:")
        Y = int(input())
        print("Enter the step for the generation of 3-SAT problems (useful for big benchmarks, if uneeded just enter 1):")
        step = int(input())
    else:
        print("Enter the amount of clauses for the generation of 3-SAT problems (enter above 0):")
        X = int(input())
        print("Enter the minimum number of variables for the generation of 3-SAT problems (enter 3 or above:")
        Z = int(input())
        print("Enter the maximum number of variables for the generation of 3-SAT problems:")
        Y = int(input())
        print(
            "Enter the step for the generation of 3-SAT problems (useful for big benchmarks, if uneeded just enter 1):")
        step = int(input())
    print("turn on resolution? y/n:")
    rezol = input()
    generate_3sat_tests(X,Y,Z,step,TEST)
    print("test_input")
    print(test_input)
    print("tests")
    print(tests)
    i = 0
    j = 0
    alg_chooser = ["DPLL", "DP"]
    if rezol == "y" or rezol == "Y":
        alg_chooser.append("RES")
    print(f"{'Algorithm':<8}     {'Test':<15}     {'Time (s)':<12}{'Peak mem (KB)':<12}     {'satisfiability'}     {'variables'}     {'clauses'}     {'ratio'}")
    for name, cnf in tests:
        for alg in alg_chooser:
            try:
                res = measure_performance(alg, cnf)
                if alg == "DPLL":
                    actual = dpll([frozenset(c) for c in cnf]) is not None
                elif alg == "DP":
                    actual = davis_putnam([frozenset(c) for c in cnf])[1]
                else:
                    actual = resolution_solver([frozenset(c) for c in cnf])[1]
                    if isinstance(actual, str):
                        actual = None

                ratio = test_input[i][1]/test_input[i][0]
                benchmark_results.append({
                    "Algorithm": alg,
                    "Test Case": name,
                    "Variables": test_input[i][0],
                    "Clauses": test_input[i][1],
                    "Time (s)": res['time'],
                    "Memory (KB)": res['peak_kb'],
                    "Result": actual,
                    "ratio": ratio,
                })

                latex_table = tabulate(
                    benchmark_results,
                    headers="keys",
                    tablefmt="latex_booktabs",
                    floatfmt=("", "", ".0f",".0f", ".6f", ".2f", "", ".2f"),
                    showindex=False
                )

                with open("benchmark_table.tex", "w") as f:
                    f.write(latex_table)
                print("LaTeX table generated: benchmark_table.tex")
                if TEST == "y" or TEST == "Y":
                    print(
                    f"{alg:<8}  {name:<20}    {res['time']:.6f}    {res['peak_kb']:.2f}               {actual}               {test_input[i][0]:<10}     {test_input[i][1]}          {ratio:.2f}")
                else:
                    print(
                        f"{alg:<8}  {name:<20}    {res['time']:.6f}    {res['peak_kb']:.2f}               {actual}               {test_input[i][0]:<10}     {test_input[i][1]}          {ratio:.2f}")
                j += 1
                if rezol == "y" or rezol == "Y":
                    if j % 3 == 0:
                        i += 1
                else:
                    if j % 2 == 0:
                        i += 1
            except Exception as e:
                print(f"{alg:<8} {name:<20} ERROR: {str(e)}")
                print("note: if its the last test it doesnt affect the benchmark")
                benchmark_results.append({
                    "Algorithm": alg,
                    "Test Case": name,
                    "Error": str(e)
                })

