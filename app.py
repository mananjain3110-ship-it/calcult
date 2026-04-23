import streamlit as st
import pandas as pd

st.title("💰 Advanced Income Tax Calculator (India)")

# -------------------------------
# 1. Assessee Details
# -------------------------------
name = st.text_input("Name of Assessee")

assessee_type = st.selectbox(
    "Assessee Type",
    ["Individual", "Partnership Firm", "Company"]
)

age = 0
if assessee_type == "Individual":
    age = st.number_input("Enter Age", min_value=0)

# -------------------------------
# 2. Income Inputs
# -------------------------------
st.subheader("📊 Income Details")

salary = st.number_input("Salary", 0)
house = st.number_input("House Property", 0)
business = st.number_input("Business Income", 0)
capital = st.number_input("Capital Gains (Special Rate)", 0)
other = st.number_input("Other Income", 0)

gross_income = salary + house + business + other
deductions = st.number_input("Deductions (Old Regime)", 0)

# -------------------------------
# 3. Slab Selection (Age Based)
# -------------------------------
def basic_exemption(age):
    if age >= 80:
        return 500000
    elif age >= 60:
        return 300000
    else:
        return 250000

# -------------------------------
# 4. Tax Calculation
# -------------------------------
def old_tax(income):
    tax = 0
    basic = basic_exemption(age)

    if income > basic:
        slab = min(income - basic, 250000)
        tax += slab * 0.05

    if income > 500000:
        slab = min(income - 500000, 500000)
        tax += slab * 0.20

    if income > 1000000:
        tax += (income - 1000000) * 0.30

    return tax


def new_tax(income):
    tax = 0
    slabs = [(300000,0),(600000,0.05),(900000,0.10),(1200000,0.15),(1500000,0.20),(float('inf'),0.30)]
    prev = 0

    for limit, rate in slabs:
        if income > prev:
            taxable = min(income, limit) - prev
            tax += taxable * rate
        prev = limit

    return tax

# -------------------------------
# 5. Capital Gain Tax (Flat)
# -------------------------------
def capital_gain_tax(cg):
    return cg * 0.15   # simplified (STCG example)

# -------------------------------
# 6. Surcharge + Marginal Relief
# -------------------------------
def surcharge_with_relief(tax, income):
    surcharge = 0

    if income > 5000000:
        surcharge = tax * 0.10

        # Marginal Relief
        excess_income = income - 5000000
        excess_tax = (tax + surcharge) - tax
        if excess_tax > excess_income:
            surcharge -= (excess_tax - excess_income)

    return surcharge

# -------------------------------
# 7. Compute
# -------------------------------
if st.button("Calculate Tax"):

    # Taxable Income
    old_income = gross_income - deductions - 50000
    new_income = gross_income - 50000

    old_tax_amt = old_tax(old_income)
    new_tax_amt = new_tax(new_income)

    # Add Capital Gains Tax
    cg_tax = capital_gain_tax(capital)

    old_tax_amt += cg_tax
    new_tax_amt += cg_tax

    # -------------------------------
    # Rebate u/s 87A
    # -------------------------------
    if assessee_type == "Individual":
        if old_income <= 500000:
            old_tax_amt = 0
        if new_income <= 700000:
            new_tax_amt = 0

    # -------------------------------
    # Surcharge
    # -------------------------------
    old_surcharge = surcharge_with_relief(old_tax_amt, old_income)
    new_surcharge = surcharge_with_relief(new_tax_amt, new_income)

    # -------------------------------
    # Cess
    # -------------------------------
    old_total = old_tax_amt + old_surcharge
    new_total = new_tax_amt + new_surcharge

    old_cess = old_total * 0.04
    new_cess = new_total * 0.04

    final_old = old_total + old_cess
    final_new = new_total + new_cess

    # -------------------------------
    # Output
    # -------------------------------
    st.subheader("📑 Summary")

    st.write(f"Gross Income: ₹ {gross_income:,.2f}")
    st.write(f"Old Regime Tax: ₹ {final_old:,.2f}")
    st.write(f"New Regime Tax: ₹ {final_new:,.2f}")

    # Best Option
    if final_old < final_new:
        st.success(f"Old Regime Better (Save ₹ {final_new-final_old:,.2f})")
    else:
        st.success(f"New Regime Better (Save ₹ {final_old-final_new:,.2f})")

    # -------------------------------
    # Chart
    # -------------------------------
    data = pd.DataFrame({
        "Regime": ["Old", "New"],
        "Tax": [final_old, final_new]
    })

    st.bar_chart(data.set_index("Regime"))
    st.subheader("💳 Tax Payment Details")

advance_tax = st.number_input("Advance Tax Paid (₹)", min_value=0)
tds = st.number_input("TDS/TCS (₹)", min_value=0)

months_delay_234A = st.number_input("Delay in Filing Return (Months) - 234A", min_value=0)
# -------------------------------
# Interest u/s 234B
# -------------------------------
def interest_234B(tax_payable, advance_tax):
    if advance_tax >= 0.9 * tax_payable:
        return 0
    shortfall = tax_payable - advance_tax
    return shortfall * 0.01 * 12   # assumed 12 months


# -------------------------------
# Interest u/s 234C (Simplified)
# -------------------------------
def interest_234C(tax_payable, advance_tax):
    # Simplified flat estimate (not installment-wise)
    if advance_tax >= tax_payable:
        return 0
    shortfall = tax_payable - advance_tax
    return shortfall * 0.01 * 3   # approx


# -------------------------------
# Interest u/s 234A
# -------------------------------
def interest_234A(tax_payable, months):
    return tax_payable * 0.01 * months
    # Net Tax Payable
net_old_tax = final_old - advance_tax - tds
net_new_tax = final_new - advance_tax - tds

# -------------------------------
# Interest Calculation
# -------------------------------
old_234B = interest_234B(final_old, advance_tax)
old_234C = interest_234C(final_old, advance_tax)
old_234A = interest_234A(final_old, months_delay_234A)

new_234B = interest_234B(final_new, advance_tax)
new_234C = interest_234C(final_new, advance_tax)
new_234A = interest_234A(final_new, months_delay_234A)

# Total Interest
total_old_interest = old_234A + old_234B + old_234C
total_new_interest = new_234A + new_234B + new_234C

# Final Payable
final_old_payable = net_old_tax + total_old_interest
final_new_payable = net_new_tax + total_new_interest


# -------------------------------
# Display
# -------------------------------
st.subheader("📑 Final Tax Liability")

st.write("### Old Regime")
st.write(f"Tax After Credits: ₹ {net_old_tax:,.2f}")
st.write(f"Interest (234A+B+C): ₹ {total_old_interest:,.2f}")
st.write(f"Final Payable: ₹ {final_old_payable:,.2f}")

st.write("### New Regime")
st.write(f"Tax After Credits: ₹ {net_new_tax:,.2f}")
st.write(f"Interest (234A+B+C): ₹ {total_new_interest:,.2f}")
st.write(f"Final Payable: ₹ {final_new_payable:,.2f}")
