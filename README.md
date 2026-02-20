# Benders Decomposition – Two-Stage Linear Optimization (Pyomo)

This project implements a **manual Benders Decomposition algorithm** for a simple two-stage linear programming problem using **Pyomo** and the **GLPK solver**.

The goal is to demonstrate how Benders cuts are generated iteratively using dual variables from the second-stage (recourse) problem.

---

## Problem Structure

The model is split into:

### First Stage (Master Problem)

Decision variable:
- `x ≥ 0`

Objective:
\[
\min \; -\frac{1}{4}x + \alpha
\]

Subject to:
- \( x \le 16 \)
- Benders optimality cuts:
\[
\alpha \ge \Phi^k + \lambda^k (x - \hat{x}^k)
\]

where:
- \( \Phi^k \) = second-stage objective value
- \( \lambda^k \) = dual multiplier
- \( \hat{x}^k \) = first-stage solution from iteration k

---

### Second Stage (Recourse Problem)

Given \( x = \hat{x} \), solve:

Decision variables:
- \( x ≥ 0 \)
- \( y ≥ 0 \)

Objective:
\[
\min -y
\]

Subject to:
- \( y - x \le 5 \)
- \( 2y - x \le 15 \)
- \( 2y + x \le 35 \)
- \( -y + x \le 10 \)
- \( x = \hat{x} \)

The dual of the linking constraint is used to construct Benders cuts.

---

## Algorithm Workflow

For a fixed number of iterations:

1. Solve first-stage master problem
2. Fix \( x = \hat{x} \)
3. Solve second-stage problem
4. Extract:
   - Second-stage objective value
   - Dual multiplier
5. Add new Benders cut to master problem
6. Update upper and lower bounds
7. Repeat

A convergence plot of Upper Bound (UB) and Lower Bound (LB) is generated.

---

## Requirements

- Python 3.9+
- Pyomo
- NumPy
- Matplotlib
- GLPK solver
## Convergence plot
Plot is in a pdf file with name Benders_convergence_plot.pdf

