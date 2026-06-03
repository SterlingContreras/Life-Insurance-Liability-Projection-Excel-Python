# Load packages
import pandas as pd
import matplotlib.pyplot as plt

# Import mortality data
mortality = pd.read_csv(
    "data/mortalitytable.csv",
    skiprows=3,
    header=None
)

# Rename columns
mortality = mortality.reset_index(drop=True)

mortality.columns = [
    "Age",
    "Male_qx",
    "Male_lx",
    "Male_ex",
    "Female_qx",
    "Female_lx",
    "Female_ex"
]

# Clean numeric fields
mortality["Age"] = pd.to_numeric(mortality["Age"])
mortality["Male_qx"] = pd.to_numeric(mortality["Male_qx"])
mortality["Female_qx"] = pd.to_numeric(mortality["Female_qx"])

mortality["Male_lx"] = pd.to_numeric(
    mortality["Male_lx"].str.replace(",", "")
)

mortality["Female_lx"] = pd.to_numeric(
    mortality["Female_lx"].str.replace(",", "")
)

# Projection assumptions
issue_age = 40
n_policies = 1000
death_benefit = 100000
interest = 0.03
term = 20

# Create projection dataset
proj = mortality[
    (mortality["Age"] >= issue_age) &
    (mortality["Age"] < issue_age + term)
].copy()

proj = proj.reset_index(drop=True)

# Initialize projection columns
proj["Lives"] = 0.0
proj["Deaths"] = 0.0

proj.loc[0, "Lives"] = n_policies

# Project survival and mortality
for t in range(len(proj)):

    qx = proj.loc[t, "Male_qx"]

    if t > 0:
        proj.loc[t, "Lives"] = (
            proj.loc[t - 1, "Lives"]
            * (1 - proj.loc[t - 1, "Male_qx"])
        )

    proj.loc[t, "Deaths"] = (
        proj.loc[t, "Lives"] * qx
    )

# Calculate expected benefit payments
proj["Benefits"] = (
    proj["Deaths"] * death_benefit
)

# Calculate present value factors
proj["t"] = range(len(proj))

proj["Discount_Factor"] = (
    1 / (1 + interest) ** proj["t"]
)

# Calculate present value of benefits
proj["PV_Benefits"] = (
    proj["Benefits"] * proj["Discount_Factor"]
)

# Calculate total liability
total_liability = proj["PV_Benefits"].sum()

# Calculate survival rates
proj["Survival_Rate"] = (
    proj["Lives"] / n_policies
)

# Survival curve
plt.plot(
    proj["Age"],
    proj["Survival_Rate"]
)

plt.title(
    "Term Life Portfolio Survival Curve"
)

plt.xlabel("Age")
plt.ylabel("Survival Rate")

plt.savefig(
    "output/survival_curve.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# Expected deaths by age
plt.plot(
    proj["Age"],
    proj["Deaths"]
)

plt.title(
    "Expected Deaths by Age"
)

plt.xlabel("Age")
plt.ylabel("Expected Deaths")

plt.savefig(
    "output/expected_deaths.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# Interest rate sensitivity analysis
sensitivity_results = []

for r in [0.02, 0.03, 0.04]:

    discount_factor = (
        1 / (1 + r) ** proj["t"]
    )

    pv = (
        proj["Benefits"]
        * discount_factor
    ).sum()

    sensitivity_results.append({
        "Interest_Rate": r,
        "PV_Liability": pv
    })

for r in [0.02, 0.03, 0.04]:

    discount_factor = (
        1 / (1 + r) ** proj["t"]
    )

    pv = (
        proj["Benefits"]
        * discount_factor
    ).sum()

    print(
        f"Interest Rate: {r:.0%}"
    )

    print(
        f"PV Liability: ${pv:,.2f}"
    )
sensitivity_df = pd.DataFrame(
    sensitivity_results
)

sensitivity_df["Interest_Rate"] = (
    sensitivity_df["Interest_Rate"] * 100
)
sensitivity_df.to_excel(
    "output/sensitivity_analysis.xlsx",
    index=False
)
plt.plot(
    sensitivity_df["Interest_Rate"],
    sensitivity_df["PV_Liability"]
)

plt.title(
    "Liability Sensitivity to Interest Rates"
)

plt.xlabel(
    "Interest Rate (%)"
)

plt.ylabel(
    "Present Value Liability"
)

plt.savefig(
    "output/liability_sensitivity.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# Export projection results
proj.to_excel(
    "output/liability_projection.xlsx",
    index=False
)
# Liability Cash Flow Chart
# Liability Cash Flow Chart
plt.plot(
    proj["Age"],
    proj["PV_Benefits"]
)

plt.title(
    "Present Value of Expected Benefit Payments"
)

plt.xlabel("Age")
plt.ylabel("PV of Benefits")

plt.savefig(
    "output/pv_liability_curve.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

#Mortality Sensitivity Scenarios
mortality_sensitivity = []

for factor in [0.90, 1.00, 1.10]:

    lives = n_policies
    pv_total = 0

    for t in range(len(proj)):

        stressed_qx = (
            proj.loc[t, "Male_qx"]
            * factor
        )

        deaths = lives * stressed_qx

        benefit = deaths * death_benefit

        discount_factor = (
            1 / (1 + interest) ** t
        )

        pv_total += (
            benefit * discount_factor
        )

        lives = (
            lives
            * (1 - stressed_qx)
        )

    mortality_sensitivity.append({
        "Mortality_Factor": factor,
        "PV_Liability": pv_total
    })

mortality_df = pd.DataFrame(
    mortality_sensitivity
)

mortality_df["Scenario"] = [
    "Low Mortality",
    "Base",
    "High Mortality"
]


plt.plot(
    mortality_df["Scenario"],
    mortality_df["PV_Liability"]
)

plt.title(
    "Liability Sensitivity to Mortality"
)

plt.xlabel(
    "Mortality Scenario"
)

plt.ylabel(
    "Present Value Liability"
)

plt.savefig(
    "output/mortality_sensitivity.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

mortality_df.to_excel(
    "output/mortality_sensitivity.xlsx",
    index=False
)
# Summary results
results = {
    "Issue Age": issue_age,
    "Policies": n_policies,
    "Death Benefit": death_benefit,
    "Interest Rate": interest,
    "Term": term,
    "PV Liability": total_liability
}

print(results)
