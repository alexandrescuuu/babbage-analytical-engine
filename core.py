from fractions import Fraction
from math import comb
import pandas as pd


OPERATIONS = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "×": lambda x, y: x * y,
    "÷": lambda x, y: x / y,
}


def bernoulli_exact(m: int) -> list[Fraction]:
    """Computes exact Bernoulli numbers B_0 ... B_m using arbitrary-precision Fractions."""
    B = [Fraction(1)]
    for k in range(1, m + 1):
        B.append(-sum(comb(k + 1, j) * B[j] for j in range(k)) / (k + 1))
    return B


def bernoulli_float(m: int) -> list[float]:
    """Computes Bernoulli numbers using standard IEEE-754 64-bit floats (shows overflow/NaN)."""
    B = [1.0]
    for k in range(1, m + 1):
        try:
            val = -sum(comb(k + 1, j) * B[j] for j in range(k)) / (k + 1)
            B.append(val)
        except OverflowError:
            B.append(float("nan"))
    return B


def get_setup_ops(bug_1843: bool = False):
    """Operations 1 to 12 of Ada Lovelace's Note G diagram."""
    op4 = (4, "÷", "V5", "V4", ["V11"]) if bug_1843 else (4, "÷", "V4", "V5", ["V11"])
    return [
        (1, "×", "V2", "V3", ["V4", "V5", "V6"]),
        (2, "-", "V4", "V1", ["V4"]),
        (3, "+", "V5", "V1", ["V5"]),
        op4,
        (5, "÷", "V11", "V2", ["V11"]),
        (6, "-", "V13", "V11", ["V13"]),
        (7, "-", "V3", "V1", ["V10"]),
        (8, "+", "V2", "V7", ["V7"]),
        (9, "÷", "V6", "V7", ["V11"]),
        (10, "×", "V21", "V11", ["V12"]),
        (11, "+", "V12", "V13", ["V13"]),
        (12, "-", "V10", "V1", ["V10"]),
    ]


def get_loop_ops(vB: str):
    """Operations 13 to 23 (loop body computing A_{2k+1} * B_{2k+1})."""
    return [
        (13, "-", "V6", "V1", ["V6"]),
        (14, "+", "V1", "V7", ["V7"]),
        (15, "÷", "V6", "V7", ["V8"]),
        (16, "×", "V8", "V11", ["V11"]),
        (17, "-", "V6", "V1", ["V6"]),
        (18, "+", "V1", "V7", ["V7"]),
        (19, "÷", "V6", "V7", ["V9"]),
        (20, "×", "V9", "V11", ["V11"]),
        (21, "×", vB, "V11", ["V12"]),
        (22, "+", "V12", "V13", ["V13"]),
        (23, "-", "V10", "V1", ["V10"]),
    ]


class AnalyticalEngine:
    """Emulates Babbage's Analytical Engine (Store + Mill architecture)."""

    def __init__(self, n_target: int, known_B: list[Fraction]):
        self.n = n_target
        self.store = {f"V{i}": Fraction(0) for i in range(1, 21 + n_target)}
        self.store["V1"] = Fraction(1)
        self.store["V2"] = Fraction(2)
        self.store["V3"] = Fraction(n_target)
        for i, b in enumerate(known_B):
            self.store[f"V{21 + i}"] = b
        self.trace = []

    def execute_op(self, op):
        num, operator, v1, v2, destinations = op
        result = OPERATIONS[operator](self.store[v1], self.store[v2])
        for dest in destinations:
            self.store[dest] = result
        self.trace.append({
            "Op #": num,
            "Mill Op": operator,
            "Var 1": v1,
            "Var 2": v2,
            "Write To": ", ".join(destinations),
            "Result (Exact)": str(result),
            "Approx (Float)": round(float(result), 6),
        })

    def run_note_g(self, bug_1843: bool = False) -> Fraction:
        res_var = f"V{20 + self.n}"
        for op in get_setup_ops(bug_1843=bug_1843):
            self.execute_op(op)

        k = 0
        while self.store["V10"] > 0:
            for op in get_loop_ops(f"V{22 + k}"):
                self.execute_op(op)
            k += 1

        self.execute_op((24, "-", res_var, "V13", [res_var]))
        self.execute_op((25, "+", "V1", "V3", ["V3"]))
        return self.store[res_var]


def compute_sequence(max_n: int, bug_1843: bool = False):
    """Computes B_1, B_3, ..., B_{2*max_n - 1} iteratively on the Analytical Engine."""
    known_exact = []
    known_run = []
    rows = []

    for n in range(1, max_n + 1):
        engine_exact = AnalyticalEngine(n, known_exact)
        val_exact = engine_exact.run_note_g(bug_1843=False)
        known_exact.append(val_exact)

        engine_run = AnalyticalEngine(n, known_run)
        val_run = engine_run.run_note_g(bug_1843=bug_1843)
        known_run.append(val_run)

        rows.append({
            "n": n,
            "Lovelace Index": f"B_{2*n - 1}",
            "Modern Index": f"B_{2*n}",
            "Exact Value": str(val_exact),
            "Engine Output": str(val_run),
            "Float Approx": float(val_run),
            "Mill Operations": len(engine_run.trace),
        })

    return pd.DataFrame(rows), engine_run
