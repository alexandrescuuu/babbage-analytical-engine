import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from core import compute_sequence, bernoulli_exact, bernoulli_float

st.set_page_config(
    page_title="Babbage Analytical Engine Emulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Babbage's Analytical Engine & Ada Lovelace's Note G")
st.markdown(
    "Cycle-accurate emulator of Charles Babbage's **Store & Mill** architecture executing "
    "Ada Lovelace's 1843 Bernoulli number algorithm — including the famous **Operation 4 bug**."
)

# Sidebar controls
st.sidebar.header("Engine Controls")
max_n = st.sidebar.slider("Compute up to B_{2n-1} (n)", min_value=1, max_value=10, value=4)
bug_1843 = st.sidebar.toggle(
    "Inject 1843 Publication Bug (Op 4: V5 ÷ V4)",
    value=False,
    help="In the original 1843 printed table, Operation 4 was inverted as V5 ÷ V4 instead of V4 ÷ V5.",
)

df_results, last_engine = compute_sequence(max_n=max_n, bug_1843=bug_1843)
last_row = df_results.iloc[-1]

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Target Bernoulli", f"{last_row['Lovelace Index']} ({last_row['Modern Index']})")
col2.metric("Engine Output", last_row["Engine Output"])
col3.metric("Exact Mathematical Value", last_row["Exact Value"])
col4.metric("Mill Operations Executed", int(last_row["Mill Operations"]))

if bug_1843:
    st.error(
        "**1843 Bug Active:** Operation 4 computed `(2n+1)/(2n-1)` instead of `(2n-1)/(2n+1)`. "
        "Notice how the error compounds exponentially across subsequent Bernoulli numbers!"
    )

tab1, tab2, tab3, tab4 = st.tabs([
    "Bernoulli Sequence & Complexity",
    "Mill Execution Trace",
    "Store Registers (V1...Vn)",
    "Exact Fractions vs IEEE-754 Float",
])

with tab1:
    st.subheader("Iterative Computation Results")
    st.dataframe(df_results, use_container_width=True)

    fig, ax = plt.subplots(figsize=(7, 3.2), dpi=120)
    ax.plot(df_results["n"], df_results["Mill Operations"], marker="o", color="#FF4B4B", lw=2)
    ax.set_xlabel("Iteration n")
    ax.set_ylabel("Mill Operations Count")
    ax.set_title("Linear Complexity per Step: 11n - 8 Operations (O(n^2) Cumulative)")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader(f"Step-by-Step Mill Trace for n = {max_n} ({last_row['Lovelace Index']})")
    st.dataframe(pd.DataFrame(last_engine.trace), use_container_width=True, height=400)

with tab3:
    st.subheader(f"Final State of Store Columns (Registers) after n = {max_n}")
    store_df = pd.DataFrame([
        {"Register": k, "Exact Fraction": str(v), "Decimal Value": float(v)}
        for k, v in last_engine.store.items()
    ])
    st.dataframe(store_df, use_container_width=True, height=400)

with tab4:
    st.subheader("Numerical Stability: Arbitrary-Precision Fractions vs 64-bit Float")
    m_limit = st.slider("Compare up to modern index B_m", min_value=20, max_value=300, value=100, step=20)
    Be = bernoulli_exact(m_limit)
    Bf = bernoulli_float(m_limit)

    comp_rows = []
    for m in range(10, m_limit + 1, 10):
        exact_f = float(Be[m]) if Be[m].numerator.bit_length() < 1020 else float("inf")
        rel_err = abs(Bf[m] - exact_f) / abs(exact_f) if exact_f != 0 and exact_f != float("inf") else float("nan")
        comp_rows.append({
            "Index": f"B_{m}",
            "Float64 Value": f"{Bf[m]:.6e}",
            "Relative Error": f"{rel_err:.2e}",
            "Numerator Digits": len(str(abs(Be[m].numerator))),
        })
    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True)
    st.info(
        "At B_300, standard 64-bit floating-point arithmetic overflows (`inf - inf = nan`), "
        "whereas exact rational arithmetic handles the 389-digit numerator without precision loss."
    )
