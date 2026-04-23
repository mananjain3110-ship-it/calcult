import streamlit as st
import pandas as pd

st.title("💰 Advanced Income Tax Calculator (India)")

# -------------------------------
# Assessee Details
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
# Income Inputs
# -------------------------------
st.subheader("📊 Income Details")

salary = st.number_input("Salary", 0)
house = st.number_input("House Property", 0)
business = st.number_input("Business Income", 0)
capital = st.number_input("Capital Gains", 0)
other = st.number_input("Other Income", 0)

gross_income = salary + house + business + other
deductions = st.number_input("Deductions (Old Regime)", 0)

# -------------------------------
# Tax Payment Inputs
# -------------------------------
st.subheader("💳 Tax Payments")

advance_tax = st.number_input("Advance Tax Paid", 0)
tds = st.number_input("TDS/TCS", 0)
months_delay = st.number_input("Delay Months (234A)", 0)

# -------------------------------
# Functions
# -------------------------------
def basic_exemption(age):
    if age >= 80:
        return 500000
    elif age >= 60:
        return 300000
    return 250000

def old_tax_calc(income):
    tax = 0
    basic = basic_exemption(age)

    if income > basic:
        tax += min(income - basic, 250000) * 0.05
    if income > 500000:
        tax += min(income - 500000, 500000) * 0.20
    if income > 1000000:
        tax += (income - 1000000) * 0.30

    return tax

def new_tax_calc(income):
    tax = 0
    slabs = [(300000,0),(600000,0.05),(900000,0.10),(1200000,0.15),(1500000,0.20),(float('inf'),0.30)]
    prev = 0
    for limit, rate in slabs:
        if income > prev:
            tax += (min(income, limit) - prev) * rate
        prev = limit
    return tax

def capital_tax(cg):
    return cg * 0.15

def surcharge(tax, income):
    if income > 5000000:
        return tax * 0.10
    return 0

def interest_234A(tax, m): return tax * 0.01 * m
def interest_234B(tax, adv): return 0 if adv >= 0.9*tax else (tax-adv)*0.01*12
def interest_234C(tax, adv): return 0 if adv >= tax else (tax-adv)*0.01*3

# -------------------------------
# MAIN CALCULATION
# -------------------------------
if st.button("Calculate Tax"):

    old_income = gross_income - deductions - 50000
    new_income = gross_income - 50000

    old_tax_amt = old_tax_calc(old_income)
    new_tax_amt = new_tax_calc(new_income)

    cg_tax = capital_tax(capital)
    old_tax_amt += cg_tax
    new_tax_amt += cg_tax

    # Rebate
    if assessee_type == "Individual":
        if old_income <= 500000: old_tax_amt = 0
        if new_income <= 700000: new_tax_amt = 0

    # Surcharge + Cess
    old_s = surcharge(old_tax_amt, old_income)
    new_s = surcharge(new_tax_amt, new_income)

    old_total = old_tax_amt + old_s
    new_total = new_tax_amt + new_s

    old_cess = old_total * 0.04
    new_cess = new_total * 0.04

    final_old = old_total + old_cess
    final_new = new_total + new_cess

    # Interest
    old_int = interest_234A(final_old, months_delay) + interest_234B(final_old, advance_tax) + interest_234C(final_old, advance_tax)
    new_int = interest_234A(final_new, months_delay) + interest_234B(final_new, advance_tax) + interest_234C(final_new, advance_tax)

    net_old = final_old - advance_tax - tds + old_int
    net_new = final_new - advance_tax - tds + new_int

    # -------------------------------
    # BREAKDOWN
    # -------------------------------
    st.subheader("📊 Detailed Breakdown")

    # OLD
    st.markdown("### 🧾 Old Regime")

    st.write(f"Gross Income: ₹ {gross_income:,.2f}")
    st.write(f"Less Deduction: ₹ {deductions:,.2f}")
    st.write(f"Taxable Income: ₹ {old_income:,.2f}")

    old_table = []
    basic = basic_exemption(age)

    if old_income > basic:
        amt = min(old_income-basic,250000)
        old_table.append(["5%", amt, amt*0.05])
    if old_income > 500000:
        amt = min(old_income-500000,500000)
        old_table.append(["20%", amt, amt*0.20])
    if old_income > 1000000:
        amt = old_income-1000000
        old_table.append(["30%", amt, amt*0.30])

    st.table(pd.DataFrame(old_table, columns=["Rate","Income","Tax"]))

    st.write(f"Capital Gain Tax: ₹ {cg_tax:,.2f}")
    st.write(f"Surcharge: ₹ {old_s:,.2f}")
    st.write(f"Cess: ₹ {old_cess:,.2f}")
    st.write(f"Interest: ₹ {old_int:,.2f}")
    st.write(f"Final Payable: ₹ {net_old:,.2f}")

    # NEW
    st.markdown("### 🧾 New Regime")

    st.write(f"Taxable Income: ₹ {new_income:,.2f}")

    new_table = []
    slabs = [(300000,0),(600000,0.05),(900000,0.10),(1200000,0.15),(1500000,0.20),(float('inf'),0.30)]
    prev = 0

    for limit, rate in slabs:
        if new_income > prev:
            amt = min(new_income, limit)-prev
            if rate>0:
                new_table.append([f"{int(rate*100)}%", amt, amt*rate])
        prev = limit

    st.table(pd.DataFrame(new_table, columns=["Rate","Income","Tax"]))

    st.write(f"Capital Gain Tax: ₹ {cg_tax:,.2f}")
    st.write(f"Surcharge: ₹ {new_s:,.2f}")
    st.write(f"Cess: ₹ {new_cess:,.2f}")
    st.write(f"Interest: ₹ {new_int:,.2f}")
    st.write(f"Final Payable: ₹ {net_new:,.2f}")

    # Comparison
    if net_old < net_new:
        st.success(f"Old Regime Better (Save ₹ {net_new-net_old:,.2f})")
    else:
        st.success(f"New Regime Better (Save ₹ {net_old-net_new:,.2f})")

    # Chart
    df = pd.DataFrame({"Regime":["Old","New"],"Tax":[net_old, net_new]})
    st.bar_chart(df.set_index("Regime"))
