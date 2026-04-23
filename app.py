import streamlit as st
import pandas as pd

# -------------------------------
# Old Regime Tax
# -------------------------------
def old_tax(income, deductions):
    taxable_income = income - deductions - 50000
    
    tax = 0
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = (250000 * 0.05) + (taxable_income - 500000) * 0.20
    else:
        tax = (250000 * 0.05) + (500000 * 0.20) + (taxable_income - 1000000) * 0.30
    
    return max(tax, 0)


# -------------------------------
# New Regime Tax
# -------------------------------
def new_tax(income):
    taxable_income = income - 50000
    
    tax = 0
    if taxable_income <= 300000:
        tax = 0
    elif taxable_income <= 600000:
        tax = (taxable_income - 300000) * 0.05
    elif taxable_income <= 900000:
        tax = (300000 * 0.05) + (taxable_income - 600000) * 0.10
    elif taxable_income <= 1200000:
        tax = (300000 * 0.05) + (300000 * 0.10) + (taxable_income - 900000) * 0.15
    elif taxable_income <= 1500000:
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (taxable_income - 1200000) * 0.20
    else:
        tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (300000 * 0.20) + (taxable_income - 1500000) * 0.30
    
    return max(tax, 0)


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("💰 Income Tax Calculator (India)")

# User Details
st.subheader("👤 Basic Details")
name = st.text_input("Enter Name of Assessee")
assessment_year = st.selectbox(
    "Select Assessment Year",
    ["AY 2024-25", "AY 2025-26"]
)

# Income Inputs
st.subheader("💼 Income Details")
income = st.number_input("Enter Annual Income (₹)", min_value=0)
deductions = st.number_input("Enter Deductions (Old Regime) (₹)", min_value=0)

if st.button("Calculate Tax"):

    old_regime_tax = old_tax(income, deductions)
    new_regime_tax = new_tax(income)

    st.subheader("📊 Tax Summary")

    st.write(f"Name: **{name}**")
    st.write(f"Assessment Year: **{assessment_year}**")

    st.write(f"Old Regime Tax: ₹ {old_regime_tax:,.2f}")
    st.write(f"New Regime Tax: ₹ {new_regime_tax:,.2f}")

    # -------------------------------
    # Better Regime
    # -------------------------------
    st.subheader("✅ Recommendation")

    if old_regime_tax < new_regime_tax:
        st.success(f"Old Regime is Better. You save ₹ {new_regime_tax - old_regime_tax:,.2f}")
    elif new_regime_tax < old_regime_tax:
        st.success(f"New Regime is Better. You save ₹ {old_regime_tax - new_regime_tax:,.2f}")
    else:
        st.info("Both Regimes are Equal")

    # -------------------------------
    # Chart
    # -------------------------------
    data = pd.DataFrame({
        'Regime': ['Old Regime', 'New Regime'],
        'Tax': [old_regime_tax, new_regime_tax]
    })

    st.subheader("📈 Tax Comparison Chart")
    st.bar_chart(data.set_index('Regime'))
