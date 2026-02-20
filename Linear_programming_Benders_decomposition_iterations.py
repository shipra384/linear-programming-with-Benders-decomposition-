import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from pyomo.opt import SolverFactory


# Mathematical formulation 1st stage
def Obj_1st(m):
    return -1/4*m.x + m.alpha

def Constraint1(m):
    return m.x <= 16

def CreateCuts(m, c):
    return m.alpha >= m.Phi[c] + m.Lambda[c]*(m.x - m.x_hat[c])

# Mathematical formulation 2nd stage
def Obj_2nd(m):
    return -m.y

def Constraint2(m):
    return m.y - m.x <= 5

def Constraint3(m):
    return 2*m.y - m.x <= 15

def Constraint4(m):
    return 2*m.y + m.x <= 35

def Constraint5(m):
    return -m.y + m.x <= 10

def Constraint6(m):
    return m.x == m.X_hat 


# Set up model 1st stage
def ModelSetUp_1st(Cuts):
    # Instance
    m = pyo.ConcreteModel()

    # Variables
    m.x = pyo.Var(within=pyo.NonNegativeReals)

    # Cuts information
    m.Cut = pyo.Set(initialize=Cuts["Set"])
    m.Phi = pyo.Param(m.Cut, initialize=Cuts["Phi"])
    m.Lambda = pyo.Param(m.Cut, initialize=Cuts["lambda"])
    m.x_hat = pyo.Param(m.Cut, initialize=Cuts["x_hat"])
    m.alpha = pyo.Var(bounds=(-25, 25))

    # Constraint cut
    m.CreateCuts = pyo.Constraint(m.Cut, rule=CreateCuts)

    # Constraints
    m.Constraint1 = pyo.Constraint(rule=Constraint1)

    # Objective function
    m.obj = pyo.Objective(rule=Obj_1st, sense=pyo.minimize)

    return m

# Set up model 2nd stage
def ModelSetUp_2nd(X_hat):
    # Instance
    m = pyo.ConcreteModel()

    # Sets
    m.X_hat = pyo.Param(initialize=X_hat)

    # Variables
    m.x = pyo.Var(within=pyo.NonNegativeReals)
    m.y = pyo.Var(within=pyo.NonNegativeReals)

    # Define Constraints
    m.Constraint2 = pyo.Constraint(rule=Constraint2)
    m.Constraint3 = pyo.Constraint(rule=Constraint3)
    m.Constraint4 = pyo.Constraint(rule=Constraint4)
    m.Constraint5 = pyo.Constraint(rule=Constraint5)
    m.Constraint6 = pyo.Constraint(rule=Constraint6)

    # Objective function
    m.obj = pyo.Objective(rule=Obj_2nd, sense=pyo.minimize)

    return m

# Solve function
def Solve(m):
    opt = SolverFactory("glpk")
    m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    results = opt.solve(m, load_solutions=True)
    return results, m
def DisplayResults(m):
    return print(m.display(), m.dual.display())

# Function for creating new linear cuts for optimization problem
def Cut_manage(Cuts, m):
    # Find cut iteration by checking number of existing cuts
    cut = len(Cuts["Set"])

    # Add new cut to list
    Cuts["Set"].append(cut)

    # Find 2nd stage cost result
    Cuts["Phi"][cut] = pyo.value(m.obj)
    Cuts["lambda"][cut] = m.dual[m.Constraint6]
    Cuts["x_hat"][cut] = m.X_hat

    return Cuts

# Main function
def main():
    # Setup for benders decomposition
    Cuts = {}
    Cuts["Set"] = []
    Cuts["Phi"] = {}
    Cuts["lambda"] = {}
    Cuts["x_hat"] = {}

    UB = {}
    LB = {}

   

    # Loop iterations
    for i in range(6):
        
        
        # Solve 1st stage problem
        m_1st = ModelSetUp_1st(Cuts)
        results, m_1st = Solve(m_1st)

        # Extract the value of m.x
        X_hat_value = m_1st.x.value
        
        #Print results 1st stage
        print("Iteration",i,"x=", m_1st.x.value)
        print("Iteration",i,"Recousre function=", m_1st.alpha.value)
        input()

        # Setup and solve 2nd stage problem
        m_2nd = ModelSetUp_2nd(X_hat_value)
        results, m_2nd = Solve(m_2nd)

        # Create new cuts for 1st stage problem
        Cuts = Cut_manage(Cuts, m_2nd)
        
        #Print results 2nd stage
        print("Iteration",i,"y=", m_2nd.y.value)
        print("Dual variable:")
        for component in Cuts:
            if component == "lambda":
                print(component,Cuts[component])
        input()
        
        # Convergence check
        print("UB:",pyo.value(pyo.value(m_1st.obj))+pyo.value(pyo.value(m_2nd.obj))-pyo.value(m_1st.alpha.value),"and LB:",pyo.value(m_1st.obj))
        UB[i] = pyo.value(pyo.value(m_1st.obj))+pyo.value(pyo.value(m_2nd.obj))-pyo.value(m_1st.alpha.value)
        LB[i] =pyo.value(pyo.value(m_1st.obj))
        
        
    # Plotting phase
    UB_values = list(UB.values())
    LB_values = list(LB.values())

    # Plot subproblem objective value against iteration count
    plt.plot(UB_values, marker='o', linestyle='-', label='Upper Bound')
    plt.plot(LB_values, marker='o', linestyle='-', label='Lower Bound')
    plt.xlabel('Iterations')
    plt.ylabel('Objective Value')
    plt.title('Benders Decomposition Convergence')
    plt.grid(True)
    plt.legend()
    #plt.show()
    plt.savefig('Benders_convergence_plot.pdf')

if __name__ == "__main__":
    main()
