import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set page title
st.title("Wealth Tax Revenue Calculator")

# Add description
st.write("""
This app shows how much government expenditure could be covered by implementing a wealth tax 
on individuals with net worth over £10 million at different tax rates.
""")

# Create a slider for tax rate (1-5%)
tax_rate = st.slider("Wealth Tax Rate (%)", min_value=1, max_value=5, value=1, step=1)

# Calculate revenue based on the 1% = £11.9bn baseline
# We're assuming a linear relationship here
revenue_billions = 11.9 * tax_rate

# Sample government expenditure data (in billions of pounds)
# You should replace this with actual UK government expenditure data
expenditure_data = {
    "Category": ["Healthcare (NHS)", "Education", "Defense", "Welfare", "Transport", 
                 "Public Order & Safety", "Housing & Environment", "Debt Interest"],
    "Amount (£bn)": [176, 103, 55, 231, 44, 38, 31, 45]
}

expenditure_df = pd.DataFrame(expenditure_data)

# Create the visualization
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the expenditure bars
bars = ax.bar(expenditure_df["Category"], expenditure_df["Amount (£bn)"], color='lightgray')

# Add a horizontal line showing wealth tax revenue
ax.axhline(y=revenue_billions, color='red', linestyle='-', linewidth=2)

# Add text label for the wealth tax line
ax.text(0, revenue_billions + 5, f"£{revenue_billions:.1f}bn from {tax_rate}% wealth tax", 
        color='red', fontweight='bold')

# Customize the chart
ax.set_ylabel("Amount (£ billions)")
ax.set_title(f"UK Government Expenditure vs. {tax_rate}% Wealth Tax Revenue")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Display the chart in Streamlit
st.pyplot(fig)

# Add additional context
st.write(f"""
### Key Findings:
- A {tax_rate}% wealth tax on individuals with net worth over £10 million would generate approximately £{revenue_billions:.1f} billion annually
- This would cover {', '.join([dept for i, dept in enumerate(expenditure_df["Category"]) if expenditure_df["Amount (£bn)"][i] <= revenue_billions])} expenditure
""")

# Add information about the data source
st.info("""
**Data Source:** The wealth tax revenue estimates are based on research from the Wealth Tax Commission, 
which found that a 1% tax on wealth above £10m would raise approximately £11.9 billion annually.
""")
