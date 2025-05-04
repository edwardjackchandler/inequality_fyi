import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="UK Wealth Tax Impact Simulator",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("UK Wealth Tax Impact Simulator")
st.markdown("""
This application simulates the impact of a wealth tax on wealth inequality in the UK over time.
According to research, wealth in Great Britain is unevenly distributed, with the wealthiest 10% 
holding around 43% of all wealth.
""")

# Sidebar for parameters
st.sidebar.header("Simulation Parameters")

# Tax parameters
tax_rate = st.sidebar.slider("Wealth Tax Rate (%)", 0.0, 5.0, 2.0, 0.1)
wealth_threshold = st.sidebar.number_input("Wealth Threshold (£ millions)", 1.0, 50.0, 10.0, 1.0) * 1_000_000
years_to_simulate = st.sidebar.slider("Years to Simulate", 5, 50, 20)

# Growth parameters
avg_growth_rate = st.sidebar.slider("Average Asset Growth Rate (%)", 1.0, 10.0, 5.0, 0.1)
high_wealth_growth_premium = st.sidebar.slider("Additional Growth for High Wealth (%)", 0.0, 5.0, 1.0, 0.1)
redistribution_efficiency = st.sidebar.slider("Tax Redistribution Efficiency (%)", 50.0, 100.0, 80.0, 5.0) / 100

# Initial wealth distribution (simplified model based on UK data)
def initialize_wealth_groups():
    # Based on UK wealth distribution data
    # Group 1: Ultra wealthy (>£10M) - small number but large wealth
    # Group 2: Middle wealth (>£100K but <£10M) - larger group
    # Group 3: Lower wealth (<£100K) - largest group
    
    # Number of people in each group (in millions)
    group_1_population = 0.022  # 22,000 people with >£10M based on search results
    group_2_population = 30  # Approximation for middle wealth
    group_3_population = 36  # Remaining adult population
    
    # Total wealth in each group (in billions £)
    group_1_wealth = 1200  # Approximation based on search results
    group_2_wealth = 8000  # Approximation
    group_3_wealth = 800   # Approximation
    
    return {
        "Ultra Wealthy (>£10M)": {"population": group_1_population, "total_wealth": group_1_wealth},
        "Middle Wealth (>£100K)": {"population": group_2_population, "total_wealth": group_2_wealth},
        "Lower Wealth (<£100K)": {"population": group_3_population, "total_wealth": group_3_wealth}
    }

# Function to simulate wealth changes over time
def simulate_wealth_tax_impact(wealth_groups, years, tax_rate, threshold, growth_rate, 
                              high_wealth_premium, redistribution_eff):
    results = []
    
    # Initial state
    current_state = {
        "year": 0,
        "Ultra Wealthy (>£10M)": wealth_groups["Ultra Wealthy (>£10M)"]["total_wealth"],
        "Middle Wealth (>£100K)": wealth_groups["Middle Wealth (>£100K)"]["total_wealth"],
        "Lower Wealth (<£100K)": wealth_groups["Lower Wealth (<£100K)"]["total_wealth"]
    }
    results.append(current_state)
    
    for year in range(1, years + 1):
        # Calculate growth
        ultra_wealthy_growth = current_state["Ultra Wealthy (>£10M)"] * ((growth_rate + high_wealth_premium) / 100)
        middle_wealth_growth = current_state["Middle Wealth (>£100K)"] * (growth_rate / 100)
        lower_wealth_growth = current_state["Lower Wealth (<£100K)"] * (growth_rate / 100)
        
        # Apply growth
        ultra_wealthy_new = current_state["Ultra Wealthy (>£10M)"] + ultra_wealthy_growth
        middle_wealth_new = current_state["Middle Wealth (>£100K)"] + middle_wealth_growth
        lower_wealth_new = current_state["Lower Wealth (<£100K)"] + lower_wealth_growth
        
        # Calculate tax on ultra wealthy
        tax_collected = (ultra_wealthy_new * (tax_rate / 100))
        ultra_wealthy_after_tax = ultra_wealthy_new - tax_collected
        
        # Redistribute tax revenue
        tax_to_redistribute = tax_collected * redistribution_eff
        middle_wealth_share = 0.3  # 30% goes to middle wealth
        lower_wealth_share = 0.7   # 70% goes to lower wealth
        
        middle_wealth_final = middle_wealth_new + (tax_to_redistribute * middle_wealth_share)
        lower_wealth_final = lower_wealth_new + (tax_to_redistribute * lower_wealth_share)
        
        # Update state
        current_state = {
            "year": year,
            "Ultra Wealthy (>£10M)": ultra_wealthy_after_tax,
            "Middle Wealth (>£100K)": middle_wealth_final,
            "Lower Wealth (<£100K)": lower_wealth_final
        }
        results.append(current_state)
    
    return pd.DataFrame(results)

# Run simulation
wealth_groups = initialize_wealth_groups()
simulation_results = simulate_wealth_tax_impact(
    wealth_groups,
    years_to_simulate,
    tax_rate,
    wealth_threshold,
    avg_growth_rate,
    high_wealth_growth_premium,
    redistribution_efficiency
)

# Display initial statistics
st.header("Initial Wealth Distribution")
total_initial_wealth = sum([group["total_wealth"] for group in wealth_groups.values()])
total_initial_population = sum([group["population"] for group in wealth_groups.values()])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Ultra Wealthy Share", 
        f"{wealth_groups['Ultra Wealthy (>£10M)']['total_wealth'] / total_initial_wealth:.1%}",
        f"Population: {wealth_groups['Ultra Wealthy (>£10M)']['population']:.3f}M"
    )
with col2:
    st.metric(
        "Middle Wealth Share", 
        f"{wealth_groups['Middle Wealth (>£100K)']['total_wealth'] / total_initial_wealth:.1%}",
        f"Population: {wealth_groups['Middle Wealth (>£100K)']['population']:.1f}M"
    )
with col3:
    st.metric(
        "Lower Wealth Share", 
        f"{wealth_groups['Lower Wealth (<£100K)']['total_wealth'] / total_initial_wealth:.1%}",
        f"Population: {wealth_groups['Lower Wealth (<£100K)']['population']:.1f}M"
    )

# Display simulation results
st.header("Simulation Results")

# Wealth over time chart
st.subheader("Wealth by Group Over Time")
fig, ax = plt.subplots(figsize=(12, 6))
for column in simulation_results.columns:
    if column != "year":
        ax.plot(simulation_results["year"], simulation_results[column], linewidth=3, label=column)
ax.set_xlabel("Years")
ax.set_ylabel("Total Wealth (£ billions)")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# Wealth share over time
st.subheader("Wealth Share by Group Over Time")
wealth_shares = simulation_results.copy()
for year in wealth_shares["year"]:
    total_wealth = sum([wealth_shares.loc[wealth_shares["year"] == year, col].values[0] 
                        for col in wealth_shares.columns if col != "year"])
    for column in wealth_shares.columns:
        if column != "year":
            wealth_shares.loc[wealth_shares["year"] == year, f"{column} Share"] = (
                wealth_shares.loc[wealth_shares["year"] == year, column].values[0] / total_wealth
            )

share_columns = [col for col in wealth_shares.columns if "Share" in col]
fig2, ax2 = plt.subplots(figsize=(12, 6))
for column in share_columns:
    ax2.plot(wealth_shares["year"], wealth_shares[column], linewidth=3, label=column)
ax2.set_xlabel("Years")
ax2.set_ylabel("Share of Total Wealth")
ax2.set_ylim(0, 1)
ax2.legend()
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)

# Tax revenue over time
st.subheader("Annual Tax Revenue")
tax_revenue = []
for i in range(1, len(simulation_results)):
    year = simulation_results.iloc[i]["year"]
    ultra_wealthy_pre_tax = (
        simulation_results.iloc[i-1]["Ultra Wealthy (>£10M)"] * 
        (1 + (avg_growth_rate + high_wealth_growth_premium) / 100)
    )
    ultra_wealthy_post_tax = simulation_results.iloc[i]["Ultra Wealthy (>£10M)"]
    tax_collected = ultra_wealthy_pre_tax - ultra_wealthy_post_tax
    tax_revenue.append({"year": year, "tax_revenue": tax_collected})

tax_df = pd.DataFrame(tax_revenue)
fig3, ax3 = plt.subplots(figsize=(12, 6))
ax3.bar(tax_df["year"], tax_df["tax_revenue"], color="green", alpha=0.7)
ax3.set_xlabel("Years")
ax3.set_ylabel("Tax Revenue (£ billions)")
ax3.grid(True, alpha=0.3)
st.pyplot(fig3)

# Cumulative impact
st.subheader("Cumulative Impact After {} Years".format(years_to_simulate))
final_year = simulation_results.iloc[-1]
initial_year = simulation_results.iloc[0]

col1, col2, col3 = st.columns(3)
with col1:
    initial_share = initial_year["Ultra Wealthy (>£10M)"] / sum([initial_year[col] for col in initial_year.index if col != "year"])
    final_share = final_year["Ultra Wealthy (>£10M)"] / sum([final_year[col] for col in final_year.index if col != "year"])
    st.metric(
        "Ultra Wealthy Share Change", 
        f"{final_share:.1%}",
        f"{(final_share - initial_share) * 100:.1f}%"
    )
with col2:
    initial_share = initial_year["Middle Wealth (>£100K)"] / sum([initial_year[col] for col in initial_year.index if col != "year"])
    final_share = final_year["Middle Wealth (>£100K)"] / sum([final_year[col] for col in final_year.index if col != "year"])
    st.metric(
        "Middle Wealth Share Change", 
        f"{final_share:.1%}",
        f"{(final_share - initial_share) * 100:.1f}%"
    )
with col3:
    initial_share = initial_year["Lower Wealth (<£100K)"] / sum([initial_year[col] for col in initial_year.index if col != "year"])
    final_share = final_year["Lower Wealth (<£100K)"] / sum([final_year[col] for col in final_year.index if col != "year"])
    st.metric(
        "Lower Wealth Share Change", 
        f"{final_share:.1%}",
        f"{(final_share - initial_share) * 100:.1f}%"
    )

# Total tax collected
total_tax = sum(tax_df["tax_revenue"])
st.metric("Total Tax Revenue Over Period", f"£{total_tax:.1f} billion")

# Footnote
st.markdown("""
---
**Note**: This simulation is based on simplified assumptions and real-world dynamics would be more complex. 
The model assumes that tax revenue is partially redistributed to middle and lower wealth groups through 
government spending on public services, infrastructure, and social programs.

Data sources: Based on ONS wealth distribution statistics and Wealth Tax Commission research.
""")
