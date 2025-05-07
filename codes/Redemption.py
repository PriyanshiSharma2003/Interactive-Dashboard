import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
import os

access_level = int(os.getenv("ACCESS_LEVEL", "0"))

st.set_page_config(page_title="Registration Dashboard",layout="wide")

# Load external CSS
with open("C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\style.css") as f:
    custom_css = f.read()

# Custom CSS for Background and Styling
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Load Data
def load_data():
    df = pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Redemptions_Sample.csv')
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M', errors='coerce')
    return df


def download_button(df, filename, fig=None):
    # Prepare CSV
    csv_output = BytesIO()
    df.to_csv(csv_output, index=False)
    csv_b64 = base64.b64encode(csv_output.getvalue()).decode()

    # Prepare Excel
    excel_output = BytesIO()
    with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_b64 = base64.b64encode(excel_output.getvalue()).decode()

    # Prepare PDF using fpdf2
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Add header
    pdf.cell(200, 10, txt="Transaction Report", ln=True, align='C')

    # Calculate column widths based on the longest header
    col_widths = [pdf.get_string_width(col) + 10 for col in df.columns]
    row_height = 10

    # Set table header
    pdf.set_font("Arial", size=10, style='B')  # Bold for headers
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], row_height, col, border=1, align='C')
    pdf.ln()  # Move to the next line

    # Add table rows
    pdf.set_font("Arial", size=10)
    for i, row in df.iterrows():
        for j, value in enumerate(row):
            pdf.cell(col_widths[j], row_height, str(value), border=1, align='C')
        pdf.ln()

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_b64 = base64.b64encode(pdf_output.getvalue()).decode()


    # HTML with download button positioned to the right of the chart
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


def format_number(number):
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)

col1, col2 = st.columns([2, 2]) 
 
# Calculations for the metrics
total_redemption = filtered_df['orderID'].count()
total_redemption = format_number(total_redemption)
total_reward_points = filtered_df['rewardPoints'].sum()
total_reward_points = format_number(total_reward_points)
unique_redemptions = filtered_df['orderID'].nunique()
unique_redemptions = format_number(unique_redemptions)
active_members = filtered_df['memberName'].nunique()
active_members = format_number(active_members)
platinum_members = filtered_df[filtered_df['memberTier'] == 'Platinum']['memberName'].nunique()
platinum_members = format_number(platinum_members)
gold_members = filtered_df[filtered_df['memberTier'] == 'Gold']['memberName'].nunique()
gold_members = format_number(gold_members)

st.markdown("", unsafe_allow_html=True)
with col1:
    st.markdown(
        f"""
        <div class='metric-container' style="display: flex; justify-content: space-between; width: 100%; max-width: 900px; margin-bottom: 20px;">
                <div class='metric-box'>
                    <div class='metric-value'>{total_redemption}</div>
                    <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Redemption</div>
                </div>
                <div class='metric-box'>
                    <div class='metric-value'>{total_reward_points}</div>
                    <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Redeemed Points</div>
                </div>
                <div class='metric-box'>
                    <div class='metric-value'>{unique_redemptions}</div>
                    <div class='metric-label' style="font-size: 18px; font-weight: bold;">Unique Redemption</div>
                </div>
            </div>
            <div class='metric-container' style="display: flex; justify-content: space-between; width: 100%; max-width: 900px;">
                <div class='metric-box'>
                    <div class='metric-value'>{active_members}</div>
                    <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Active Members</div>
                </div>
                <div class='metric-box'>
                    <div class='metric-value'>{platinum_members}</div>
                    <div class='metric-label' style="font-size: 18px; font-weight: bold;">Platinum Members</div>
                </div>
                <div class='metric-box'>
                    <div class='metric-value'>{gold_members}</div>
                    <div class='metric-label' style="font-size: 18px; font-weight: bold;">Gold Members</div>
                </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')

    # Drop rows with NaT in 'Date' to avoid NaT errors
    filtered_df = filtered_df.dropna(subset=['Date'])

    # Now, check if the 'Date' column is not empty before proceeding
    if not filtered_df['Date'].empty:
        # Extract month and year from the valid dates
        filtered_df['Month'] = filtered_df['Date'].dt.month
        filtered_df['Year'] = filtered_df['Date'].dt.year

        # Generate all months for the x-axis
        all_months = pd.date_range(start=filtered_df['Date'].min(), 
                                end=filtered_df['Date'].max(), freq='MS').strftime('%b %Y')

        # Group by Year and Month, and calculate Redemption count
        monthly_transactions = filtered_df.groupby(['Year', 'Month'])['orderID'].count().reset_index(name='Redemption')

        # Create 'Month-Year' column for plotting or display
        monthly_transactions['Month-Year'] = pd.to_datetime(
            monthly_transactions['Year'].astype(str) + '-' + monthly_transactions['Month'].astype(str).str.zfill(2)
        ).dt.strftime('%b %Y')

        # Verify column names after modification
        print(monthly_transactions.columns)
    else:
        # Handle the case when there are no valid dates available
        all_months = []
        monthly_transactions = pd.DataFrame()  # Empty DataFrame or handle as needed
        print("No valid date data available.")

    # Ensure all months are represented
    def fill_missing_months(data, all_months):
        data = data.set_index('Month-Year')
        data = data.reindex(all_months, fill_value=0)
        data.reset_index(inplace=True)
        data.rename(columns={'index': 'Month-Year'}, inplace=True)
        return data

    # Now, ensure that you're using the correct column names and checking for empty DataFrame
    if not monthly_transactions.empty:
        filled_monthly = fill_missing_months(monthly_transactions[['Month-Year', 'Redemption']], all_months)
    else:
        print("monthly_transactions DataFrame is empty.")
        filled_monthly = pd.DataFrame()  # Handle the empty case

    # Proceed with plotting if data exists
    if not filled_monthly.empty:
        fig1 = px.bar(
            filled_monthly,
            x='Month-Year',
            y='Redemption',
            title="Monthly Redemption",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_xaxes(type='category')

        if access_level == 1:
            download_button(filled_monthly, "download-monthly-report")
        st.plotly_chart(fig1, use_container_width=True, key='fig1')
    else:
        print("No data to display for monthly redemption.")

def calculate_insights(filtered_df):
    # 1. Total Transactions Count
    total_redemption = len(filtered_df)
    total_redemption_fmt = format_number(total_redemption)  # Formatted

    # 2. Total Points Earned
    total_points_raw = filtered_df["rewardPoints"].sum()  # Raw value
    total_points_fmt = format_number(total_points_raw)   # Formatted

    # 3. Average Burn Points per Transaction
    avg_burn_points_raw = filtered_df["rewardPoints"].mean()  # Raw
    avg_burn_points_fmt = format_number(avg_burn_points_raw)  # Formatted

    # 4. Most Active Zone
    if not filtered_df["Zone"].mode().empty:
        most_active_zone = filtered_df["Zone"].mode()[0]
    else:
        most_active_zone = "No data available"

    # 5. Top Redeemed Reward
    reward_points_grouped = filtered_df.groupby("rewardName")["rewardPoints"].sum()
    if not reward_points_grouped.empty:
        top_reward = reward_points_grouped.idxmax()
    else:
        top_reward = "No data available"

    # 6. Total Orders per Zone
    orders_per_zone = filtered_df["Zone"].value_counts().to_dict()

    # 7. Customer with Most Points Redeemed
    customer_points_grouped = filtered_df.groupby("memberName")["rewardPoints"].sum()
    if not customer_points_grouped.empty:
        top_customer = customer_points_grouped.idxmax()
    else:
        top_customer = "No data available"

    # Return both raw and formatted values
    return (
        total_redemption_fmt, total_points_fmt, total_points_raw,
        avg_burn_points_fmt, most_active_zone, top_reward, orders_per_zone, top_customer
    )

st.markdown("", unsafe_allow_html=True)
with col2:
    (
        total_redemption, total_points, total_points_raw,
        avg_burn_points, most_active_zone, top_reward, orders_per_zone, top_customer
    ) = calculate_insights(filtered_df)
    # Optional: Add a conditional line if some condition is met (example)
    tier_line = "<hr>" if total_points_raw > 10000 else ""

    # Display Insights using Streamlit
    st.markdown(
        
    f"""
    <br>
    <div class='summary-container' style="height: 715px; width: 100%; margin-top: -18px;">
        <div class='summary-box'>
            <div class='summary-value'>Insight Summary
                <div></div>
                <div class='summary-label' style="font-size: 20px;">
                    1. <b>🔢 Total Redemption:</b><br> The total number of redemptions made is <b>{total_redemption}</b>.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    2. <b>⭐ Total Reward Points:</b><br> The total number of reward points earned across all redemptions is <b>{total_points}</b> points.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    3. <b>🌍 Average Burn Points per Redemption:</b><br> The average number of points used per redemption is <b>{avg_burn_points}</b> points.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    4. <b>📊 Most Active Zone:</b><br> The zone with the most redemptions is <b>{most_active_zone}</b>.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    5. <b>🏆 Top Redeemed Reward:</b><br> The most redeemed reward is <b>{top_reward}</b>.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    6. <b>📅 Total Orders per Zone:</b><br> The total number of orders made per zone is <b>{orders_per_zone}</b>.
                </div>
                <div class='summary-label' style="font-size: 20px;">
                    7. <b>👤 Customer with Most Points Redeemed:</b><br> The customer who has redeemed the most points is <b>{top_customer}</b>.
                </div>
            </div>      
        </div>  
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        /* Target all Plotly charts only */
        [data-testid="stPlotlyChart"] {
            border-radius: 15px; /* Curved corners */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional shadow */
            overflow: hidden; /* Ensure content fits within rounded corners */
            background-color: white; /* Optional background color */
        }
    </style>
    """,
    unsafe_allow_html=True
)

col3, col4 = st.columns([2,2])

# Quaterly Chart
filtered_df['Quarter'] = filtered_df['Date'].dt.to_period('Q')
quarterly_transactions = filtered_df.groupby(filtered_df['Date'].dt.to_period('Q'))['orderID'].count().reset_index(name='Redemption')
quarterly_transactions['Quarter'] = quarterly_transactions['Date'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")
fig2 = px.bar(
    quarterly_transactions,
    x='Quarter',
    y='Redemption',
    title="Quarterly Redemption",
    color_discrete_sequence=['#F8AE54', '#B6A6E9']
)
fig2.update_xaxes(type='category')
with col3: 
    if access_level == 1:   
        download_button(quarterly_transactions, "download-quaterly-report")
    st.plotly_chart(fig2)

# Yearly Chart
yearly_transactions = filtered_df.groupby(filtered_df['Date'].dt.year)['orderID'].count().reset_index(name='Redemption')
yearly_transactions.columns = ['Year', 'Redemption']

# Creating a pie chart
fig3 = px.pie(
    yearly_transactions,
    names='Year',
    values='Redemption',
    title="Yearly Redemption Distribution",
    color='Year',
    color_discrete_sequence=['#92C5F9']
    
)
fig3.update_traces(textinfo='percent+label')
with col4:
    if access_level == 1:
        download_button(yearly_transactions, "download-yearly-report")
    st.plotly_chart(fig3)


col5, col6 = st.columns([2,2])

# Top 5 redemeed products
redemption_counts = filtered_df.groupby(['rewardName', 'memberType'])['memberID'].nunique().reset_index(name='Redemptions')
top_redemption_counts = redemption_counts.sort_values(by='Redemptions', ascending=False).head(5)

fig4 = px.bar(
    top_redemption_counts, x='rewardName', y='Redemptions', 
    color='rewardName', title='Top 5 Redemptions by Product',
    color_continuous_scale=[
                        'rgba(67, 148, 229, 0.6)',  # Light Blue
                        'rgba(135, 111, 212, 0.6)',  # Light Purple
                        'rgba(199, 199, 199, 0.6)',  # Light Gray
                        'rgba(248, 174, 84, 0.6)'   # Light Orange
                  ]
)
fig4.update_traces(textposition='outside')
with col5:
    if access_level == 1:
        download_button(top_redemption_counts, "top_product_redemption_count")
    st.plotly_chart(fig4)

# Create Tier-wise Redemptions Chart 
tier_redemptions = filtered_df.groupby('memberTier')['rewardPoints'].sum().reset_index(name='Total_Redemption_Points')
fig5 = px.bar(
    tier_redemptions, x='memberTier', y='Total_Redemption_Points', 
    color='memberTier', title='Tier-wise Redemptions',
    color_discrete_sequence = ['#B6A6E9', '#FF6F61', '#6B5B95', '#88B04B', '#FFA500', '#92A8D1'])
fig5.update_traces(textposition='outside')

with col6: 
    if access_level == 1:
        download_button(tier_redemptions, "tier_redemption")
    st.plotly_chart(fig5)

