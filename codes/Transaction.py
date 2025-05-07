import streamlit as st
import pandas as pd
import plotly.express as px
import io
import plotly.io as pio
from io import BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
import os

access_level = int(os.getenv("ACCESS_LEVEL", "0"))  # Default to "0" if not set

st.set_page_config(page_title="Transaction Dashboard", layout="wide")

# Load external CSS
with open("C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\style.css") as f:
    custom_css = f.read()

st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Transactions_sample.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M', errors='coerce')
    return df

def download_button(df, filename, fig=None):
    # Prepare CSV, Excel, and PDF as you already did
    csv_output = BytesIO()
    df.to_csv(csv_output, index=False)
    csv_b64 = base64.b64encode(csv_output.getvalue()).decode()

    excel_output = BytesIO()
    with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_b64 = base64.b64encode(excel_output.getvalue()).decode()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Transaction Report", ln=True, align='C')
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_b64 = base64.b64encode(pdf_output.getvalue()).decode()

    
    st.markdown(f"""
    <style>
        .download-container {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}
        .dropdown-container {{
            position: relative;
            display: inline-block;
        }}
        .dropdown-content {{
            display: none;
            position: absolute;
            background-color: white;
            border: 1px solid #ddd;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
            z-index: 1;
            min-width: 120px;
            right: 0; /* Align dropdown to the right */
            top: 100%; /* Position dropdown below the button */
            max-height: 200px; /* Limit dropdown height */
            overflow-y: auto; /* Add scroll if content exceeds max-height */
            white-space: nowrap; /* Prevent text wrapping */
        }}
        .dropdown-content a {{
            color: black;
            padding: 10px 12px;
            text-decoration: none;
            display: block;
            font-size: 14px;
        }}
        .dropdown-content a:hover {{
            background-color: #f4f4f4;
        }}
        .dropdown-container:hover .dropdown-content {{
            display: block;
        }}
        .dropdown-container img {{
            cursor: pointer;
            width: 16px;  /* Reduced the image size */
            height: 16px;
        }}
    </style>
    <div class="download-container">
        <div class="dropdown-container">
            <img src="data:image/jpeg;base64,{base64.b64encode(open('downloadButton.png', 'rb').read()).decode()}" alt="Download Icon">
            <div class="dropdown-content">
                <a href="data:file/csv;base64,{csv_b64}" download="{filename}.csv">Download CSV</a>
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="{filename}.xlsx">Download Excel</a>
                <a href="data:application/pdf;base64,{pdf_b64}" download="{filename}.pdf">Download PDF</a> 
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Load Data
df = load_data()
df = df.dropna(subset=['Date'])

# Function to filter the data
def filter_data(df, zone, state, city, tier, start_date=None, end_date=None):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
    if zone and zone != 'Select':
        df = df[df['Zone'] == zone]
    if state and state != 'Select':
        df = df[df['State'] == state]
    if city and city != 'Select':
        df = df[df['City'] == city]
    if tier and tier != 'Select':
        df = df[df['memberTier'] == tier]
    
    return df

# Initialize session state variables if not already initialized
for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'member_tier_filter']:
    if key not in st.session_state:
        st.session_state[key] = 'Select'

# Reset Filters Button
# col1, col2 = st.columns([5, 1])
# with col1:
#     st.title("")
# with col2:
#     if st.button("", icon=":material/restart_alt:", key="reset_emoji"):
#         for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'member_tier_filter']:
#             st.session_state[key] = 'Select'
#         st.rerun()
# Function to reset filters
def reset_filters():
    for key in ['date_filter', 'zone_filter', 'state_filter', 'city_filter', 'member_tier_filter']:
        st.session_state[key] = 'Select'

# Filters at the top
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5, reset_col = st.columns([2,2,2,2,2,1])

# Date Filter
with filter_col1:
    date_filter = st.selectbox(
        "**Select Date Range**",
        ['Select', 'Today', 'Yesterday', 'Last Week', 'Last Month', 'Last 3 Months', 'Last 12 Months', 'Custom Range'],
        key='date_filter'
    )

    start_date, end_date = None, None
    if date_filter == 'Today':
        start_date = end_date = datetime.now().date()
    elif date_filter == 'Yesterday':
        start_date = end_date = datetime.now().date() - timedelta(days=1)
    elif date_filter == 'Last Week':
        start_date = datetime.now().date() - timedelta(days=7)
        end_date = datetime.now().date()
    elif date_filter == 'Last Month':
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
    elif date_filter == 'Last 3 Months':
        start_date = datetime.now().date() - timedelta(days=90)
        end_date = datetime.now().date()
    elif date_filter == 'Last 12 Months':
        start_date = datetime.now().date() - timedelta(days=365)
        end_date = datetime.now().date()
    elif date_filter == 'Custom Range':
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=30))
        end_date = st.date_input("End Date", datetime.now().date())

# Zone Filter
with filter_col2:
    zone = st.selectbox(
        "**Select Zone**",
        options=['Select'] + sorted(df['Zone'].dropna().unique()),
        key="zone_filter"
    )

# Filter available states based on selected zone
filtered_states = df['State'].dropna().unique()
if zone != 'Select':
    filtered_states = df[df['Zone'] == zone]['State'].dropna().unique()

# State Filter
with filter_col3:
    state = st.selectbox(
        '**Select State**',
        ['Select'] + sorted(filtered_states),
        key='state_filter'
    )

# Filter available cities based on selected state
filtered_cities = df['City'].dropna().unique()
if state != 'Select':
    filtered_cities = df[df['State'] == state]['City'].dropna().unique()

# City Filter
with filter_col4:
    city = st.selectbox(
        '**Select City**',
        ['Select'] + sorted(filtered_cities),
        key='city_filter'
    )

# Member Tier Filter
with filter_col5:
    tier = st.selectbox(
        'Select Member Tier',
        ['Select'] + sorted(df['memberTier'].dropna().unique()),
        key='member_tier_filter'
    )
# Reset Filters Button
with reset_col:
    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #4a90e2; /* Blue background */
            color: white; /* White text */
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            border: none;
            transition: background 0.3s ease, color 0.3s ease; /* Smooth transition for background and text color */
            width: 100%; /* Full width of the column */
            margin-top: 28px; /* Align vertically with filters */
        }
        .stButton>button:hover {
            background-color: #357abd; /* Darker blue on hover */
            color: white; /* Ensure text remains white on hover */
        }
        .stButton>button:active {
            background-color: #357abd; /* Darker blue on click */
            color: white; /* Ensure text remains white on click */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Reset Filters 🔄", key="reset_button", on_click=reset_filters):
        pass  # The reset_filters function will handle the reset
    
# Filter data using the filter_data function
filtered_df = filter_data(df, zone, state, city, tier, start_date, end_date)


col1, col2 = st.columns([1,2])

# ALl Insigths Code
with col1:
# Insight 1: Total Transactions Count
    total_transactions = len(filtered_df)

    # Insight 2: Total Points Earned
    total_points = filtered_df["memberPoints"].sum()

    # Insight 3: Transactions by Tier (Retailer in this case)
    transactions_by_tier = len(filtered_df[filtered_df["memberTier"] == tier])

    # Insight 4: Most Active Zone
    most_active_zone = filtered_df["Zone"].mode()[0]  # Most frequent zone

    # Insight 5: Average Points per Transaction
    avg_points_per_transaction = filtered_df["memberPoints"].mean()

    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])  # Ensure it's datetime
        
    if start_date and end_date:  # Check if custom date range is selected
        # Filter by the selected date range
        filtered_date_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(start_date)) & 
                                   (filtered_df["Date"] <= pd.to_datetime(end_date))]
        transactions_per_day = filtered_date_df.groupby(filtered_date_df["Date"].dt.date)["transactionId"].nunique()
        unique_transactions_per_day = transactions_per_day.max()  # Get the max unique transactions in the custom date range
    else:  # No custom date range selected, calculate overall unique transactions
        transactions_per_day = filtered_df.groupby(filtered_df["Date"].dt.date)["transactionId"].nunique()
        unique_transactions_per_day = transactions_per_day.max()  # Get the max unique transactions overall

    daily_transaction_summary = transactions_per_day.to_dict() 

    # Dynamically generate total transaction according to the Tier
    tier_line = (
    f'<div class="summary-label" style="font-size: 18px;"><i>👤</i> <strong>Transactions for {tier} Tier:</strong> {transactions_by_tier} transactions.</div>'
    if tier
    else ""
    )

    # Display insights in a single card
    st.markdown(
    f"""
    <div class='summary-container' style="height: 620px; width: 100%; margin-top: -7px;">  
        <div class='summary-box'>  
            <div class='summary-value'>Insight Summary
                <div class='summary-label' style="font-size: 20px;">
                    <b>🔢 Total Transactions:</b><br> A total of <b>{len(filtered_df)}</b> transactions were recorded.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    <b>⭐ Total Points Earned:</b><br> The total points earned across all transactions is <b>{filtered_df["memberPoints"].sum()}</b> points.
                </div>
                {tier_line}  <!-- Conditional line -->
                <div class='summary-label' style="font-size: 20px;">
                    <b>🌍 Average Points per Transaction:</b><br> The average points earned per transaction is <b>{filtered_df["memberPoints"].mean():.2f}</b> points.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    <b>📊 Most Active Zone: </b><br> The most active zone is <b>{most_active_zone}</b>.
                </div>                
                <div class='summary-label' style="font-size: 20px;">
                    <b>📅 Unique Transactions Per Day:</b><br> The number of unique transactions completed each day is <b>{unique_transactions_per_day}</b>.
                </div>
            </div>      
        </div>  
    </div>  
    """,
    unsafe_allow_html=True,
)


# Monthly Chart
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
filtered_df['Month'] = filtered_df['Date'].dt.month
filtered_df['Year'] = filtered_df['Date'].dt.year

# Create all months for the x-axis
all_months = pd.date_range(start=filtered_df['Date'].min(), end=filtered_df['Date'].max(), freq='MS').strftime('%b %Y')
monthly_transactions = filtered_df.groupby(['Year', 'Month'])['transactionId'].count().reset_index(name='Transactions')
monthly_transactions['Month-Year'] = pd.to_datetime(monthly_transactions['Year'].astype(str) + '-' + monthly_transactions['Month'].astype(str).str.zfill(2)).dt.strftime('%b %Y')

# Ensure all months are represented
def fill_missing_months(data, all_months):
    data = data.set_index('Month-Year')
    data = data.reindex(all_months, fill_value=0)
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Month-Year'}, inplace=True)
    return data

filled_monthly = fill_missing_months(monthly_transactions[['Month-Year', 'Transactions']], all_months)

fig = px.bar(
    filled_monthly,
    x='Month-Year',
    y='Transactions',
    title="Monthly Transactions",
    color_discrete_sequence=['#AFDC8F']
)
fig.update_xaxes(type='category')

# fig1.update_traces(textposition='outside')

with col2:

    total_coupons_scanned = filtered_df['pointType'].notna().sum()

    def format_number(number):
        if number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return str(number)

    formatted_total_coupons_scanned = format_number(total_coupons_scanned)

    total_points = filtered_df['memberPoints'].sum()
    total_points = format_number(total_points)
    # Calculate total unique transactions across all data, irrespective of any filter
    total_transactions = filtered_df['transactionId'].nunique()  # Total unique transactions
    formatted_total_transactions = format_number(total_transactions)

    unique_members = filtered_df['memberID'].nunique()
    unique_members = format_number(unique_members)
    # Group by memberType and calculate sum of transactionIds
    memberType_grouped = filtered_df.groupby('memberType')['transactionId'].sum()

    registrations_df = pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Registrations_Sample.csv')
    dormant_members = registrations_df[~registrations_df['memberID'].isin(filtered_df['memberID'])]
    dormant_count = dormant_members['memberID'].nunique()
    dormant_count = format_number(dormant_count)

    st.markdown(
        f"""
        <div class="metric-container" style="display: flex; flex-wrap: wrap; justify-content: space-between;">
            <div class="metric-box" style="flex: 1 1 calc(20% - 10px); margin: 5px; text-align: center;">
                <div class='metric-value'>{formatted_total_transactions}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Total Transactions</div>
            </div>
            <div class="metric-box" style="flex: 1 1 calc(20% - 10px); margin: 5px; text-align: center;">
                <div class='metric-value'>{formatted_total_coupons_scanned}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Total Coupons Scanned</div>
            </div>
            <div class="metric-box" style="flex: 1 1 calc(20% - 10px); margin: 5px; text-align: center;">
                <div class='metric-value'>{total_points}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Total Points</div>
            </div>
            <div class="metric-box" style="flex: 1 1 calc(20% - 10px); margin: 5px; text-align: center;">
                <div class='metric-value'>{unique_members}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Unique Members Scanned</div>
            </div>
            <div class="metric-box" style="flex: 1 1 calc(20% - 10px); margin: 5px; text-align: center;">
                <div class='metric-value'>{dormant_count}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Dormant Members</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if access_level == 1:
        download_button(filled_monthly, "monthly_transactions")
    st.plotly_chart(fig, use_container_width=True, key='fig')


col3, col4 = st.columns([2,2])

# Quaterly Chart
filtered_df['Quarter'] = filtered_df['Date'].dt.to_period('Q')
quarterly_transactions = filtered_df.groupby(filtered_df['Date'].dt.to_period('Q'))['transactionId'].count().reset_index(name='Transactions')
quarterly_transactions['Quarter'] = quarterly_transactions['Date'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")
fig = px.bar(
    quarterly_transactions,
    x='Quarter',
    y='Transactions',
    title="Quarterly Transactions",
    color_discrete_sequence=['#a2d2ff']

)
fig.update_xaxes(type='category')
with col3:    
    if access_level == 1:
        download_button(quarterly_transactions, "download-reward-gold-member-point")
    st.plotly_chart(fig)

yearly_transactions = filtered_df.groupby(filtered_df['Date'].dt.year)['transactionId'].count().reset_index(name='Transactions')
yearly_transactions.columns = ['Year', 'Transactions']

# Create the pie chart
fig = px.pie(
    yearly_transactions,
    names='Year',  # The column for labels (years)
    values='Transactions',  # The column for values (transaction counts)
    title="Yearly Transactions",
    color_discrete_sequence=px.colors.qualitative.Set2
)

# Update the layout for better visualization
fig.update_traces(textinfo='percent+label')  # Show percentages and labels on the pie chart

with col4:
    if access_level == 1:
        download_button(yearly_transactions, "download-yearly-transactions")
    st.plotly_chart(fig, use_container_width=True)

col5, col6 = st.columns([2,2])

# Active Member Tier Wise
data = filtered_df[filtered_df['memberStatus'] == 'Active']
data = data.groupby('memberTier')['memberID'].nunique().reset_index(name='Active_Members')
data = data[data['Active_Members'] >= 20].nlargest(20, 'Active_Members')

fig = px.line(
        data, 
        x='memberTier', 
        y='Active_Members',
        title="Active Members by Member Tier",
        labels={'memberTier': 'Member Tier', 'Active_Members': 'Number of Active Members'},
        markers=True,
        color_discrete_sequence=px.colors.sequential.Blackbody
    )
with col5:
    if access_level == 1:
        download_button(data, "download-active-member-by-type")
    st.plotly_chart(fig)


# memberType Tier wise
data = filtered_df[filtered_df['memberType'] == 'Retailer']
data = data.groupby('memberTier')['memberID'].nunique().reset_index(name='Retailer_Members')
data = data[data['Retailer_Members'] >= 20].nlargest(20, 'Retailer_Members')

fig = px.pie(
        data, 
        names='memberTier', 
        values='Retailer_Members',
        title="Retailer Members by Tier",
        hole=0.3,
        color_discrete_sequence=['#AFDC8F', '#92C5F9', '#F8AE54','#B6A6E9']
    )
with col6:
    if access_level == 1:
        download_button(data, "download-retailer-by-tier")
    st.plotly_chart(fig)
