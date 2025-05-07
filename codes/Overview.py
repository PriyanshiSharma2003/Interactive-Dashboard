from matplotlib.pyplot import margins
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import base64
from datetime import datetime, timedelta
import os

access_level = int(os.getenv("ACCESS_LEVEL", "0"))  # Default to "0" if not set

# Set page configuration for full-width layout
st.set_page_config(page_title="Enhanced Member Registration Dashboard", layout="wide")

with open("C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\style.css") as f:
    custom_css = f.read()

st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Load csv data
registrations_df = pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Registrations_Sample.csv')  
transactions_df = pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Transactions_sample.csv')  
redemptions_df = pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Redemptions_Sample.csv')  

# Preprocessing: Convert date columns to datetime format
registrations_df['Date'] = pd.to_datetime(registrations_df['Date'], errors='coerce')
transactions_df['Date'] = pd.to_datetime(transactions_df['Date'], errors='coerce')
redemptions_df['Date'] = pd.to_datetime(redemptions_df['Date'], errors='coerce')

# Drop rows with invalid dates
registrations_df = registrations_df.dropna(subset=['Date'])
transactions_df = transactions_df.dropna(subset=['Date'])
redemptions_df = redemptions_df.dropna(subset=['Date'])

# Standardize column names for compatibility
registrations_df = registrations_df.rename(columns={'MemberTier': 'Tier'})
transactions_df = transactions_df.rename(columns={'memberTier': 'Tier'})
redemptions_df = redemptions_df.rename(columns={'memberTier': 'Tier'})

# Ensure Date columns are datetime for all datasets
registrations_df['Date'] = pd.to_datetime(registrations_df['Date'], errors='coerce')
transactions_df['Date'] = pd.to_datetime(transactions_df['Date'], errors='coerce')
redemptions_df['Date'] = pd.to_datetime(redemptions_df['Date'], errors='coerce')

# Combine datasets into a single dataframe with a Source column
combined_df = pd.concat([
    registrations_df.assign(Source='Registrations'),
    transactions_df.assign(Source='Transactions'),
    redemptions_df.assign(Source='Redemptions')
], ignore_index=True)

if 'Source' not in combined_df.columns:
    st.error("'Source' column is missing in the combined dataset.")
    st.stop()

combined_df['Date'] = pd.to_datetime(combined_df['Date'], errors='coerce')

# Function to filter data
def filter_data(df, zone=None, state=None, city=None, tier=None, start_date=None, end_date=None):
    if start_date and end_date:
        df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    if zone and zone != 'Select':
        df = df[df['Zone'] == zone]
    if state and state != 'Select':
        df = df[df['State'] == state]
    if city and city != 'Select':
        df = df[df['City'] == city]
    if tier and tier != 'Select':
        df = df[df['Tier'] == tier]
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
        options=['Select'] + sorted(combined_df['Zone'].dropna().unique()),
        key="zone_filter"
    )

# State Filter (dynamic options based on Zone)
filtered_states = combined_df['State'].dropna().unique()
if zone != 'Select':
    filtered_states = combined_df[combined_df['Zone'] == zone]['State'].dropna().unique()
with filter_col3:
    state = st.selectbox(
        '**Select State**',
        ['Select'] + sorted(filtered_states),
        key='state_filter'
    )

# City Filter (dynamic options based on State)
filtered_cities = combined_df['City'].dropna().unique()
if state != 'Select':
    filtered_cities = combined_df[combined_df['State'] == state]['City'].dropna().unique()
with filter_col4:
    city = st.selectbox(
        '**Select City**',
        ['Select'] + sorted(filtered_cities),
        key='city_filter'
    )

# Member Tier Filter
with filter_col5:
    tier = st.selectbox(
        '**Select Member Tier**',
        ['Select'] + sorted(combined_df['Tier'].dropna().unique()),
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
# Apply filters to combined_df
filtered_df = filter_data(combined_df, zone, state, city, tier, start_date, end_date)

def format_number(number):
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)



# Scorecard Calculation
def score_cards(filtered_df):
    # Split filtered_df back into individual dataframes
    filtered_registrations = filtered_df[filtered_df['Source'] == 'Registrations']
    filtered_transactions = filtered_df[filtered_df['Source'] == 'Transactions']
    filtered_redemptions = filtered_df[filtered_df['Source'] == 'Redemptions']

    # Metrics Calculation
    active_members_count = format_number(filtered_registrations[filtered_registrations['memberStatus'] == 'Active'].shape[0])
    inactive_members_count = format_number(filtered_registrations[filtered_registrations['memberStatus'] == 'Inactive'].shape[0])
    total_registration_count = format_number(filtered_registrations.shape[0])
    required_columns = ['MobileNo', 'EmailAddress', 'Address1']
    missing_columns = [col for col in required_columns if col not in filtered_registrations.columns]

    if missing_columns:
        filtered_registrations = pd.merge(
            filtered_registrations,
            registrations_df[['memberID', 'MobileNo', 'EmailAddress', 'Address1']],  # Ensure these columns exist in registrations_df
            on='memberID',
            how='left'
        )
    

    kyc_completed = filtered_registrations[required_columns].notnull().all(axis=1)
    total_members = len(filtered_registrations)
    kyc_completion_rate = (kyc_completed.sum() / total_members * 100) if total_members > 0 else 0
    
    total_transactions = format_number(filtered_transactions.shape[0])
    total_points = format_number(filtered_transactions['memberPoints'].sum())
    unique_members_scanned = format_number(filtered_transactions['memberID'].nunique())
    transaction_volume = len(filtered_transactions)
    new_total_points = filtered_transactions['memberPoints'].sum()
    average_transaction_value = (new_total_points / transaction_volume) if transaction_volume > 0 else 0

    

    total_redemptions = format_number(filtered_redemptions.shape[0])
    total_points_redeemed = filtered_redemptions['rewardPoints'].sum()
    unique_members_redeemed = format_number(filtered_redemptions['memberID'].nunique())
    total_points_available = total_points_redeemed + filtered_redemptions['balancePoints'].sum()
    point_utilization_rate = (total_points_redeemed / total_points_available * 100) if total_points_available > 0 else 0

    return f"""
    <div class='insight-container'>
        <div class='metric-container'>
            <div class='metric-box'>
                <div class='metric-value'>{total_registration_count}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Registrations</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{total_transactions}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Transactions</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{total_redemptions}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Redemptions</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{active_members_count}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Active Members</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{inactive_members_count}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Inactive Members</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{unique_members_scanned}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Unique Members Scanned</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{unique_members_redeemed}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Unique Members Redeemed</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{total_points}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Member Points</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{total_points}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Total Points Redeemed</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{kyc_completion_rate:.2f}%</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">KYC Completion Rate</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{average_transaction_value:.2f}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Avg Transactions Done</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{point_utilization_rate:.2f}%</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;">Point Utilization Rate</div>
            </div>
        </div>
    </div>
    """

# Display scorecards
st.markdown((score_cards(filtered_df)), unsafe_allow_html=True)


def download_button(df, filename):
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
    pdf.cell(200, 10, txt="Registration Report", ln=True, align='C')

    # Calculate column widths based on the longest header
    col_widths = [pdf.get_string_width(col) + 10 for col in df.columns]
    row_height = 10

    # Set table header
    pdf.set_font("Arial", size=10, style='B')  # Bold for headers
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], row_height, col, border=1, align='C')
    pdf.ln()  # Move to the next line

    # Add table rows
    pdf.set_font("Arial", size=8)
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
            <img src="data:image/png;base64,{base64.b64encode(open('downloadButton.png', 'rb').read()).decode()}" alt="Download Icon">
            <div class="dropdown-content">
                <a href="data:file/csv;base64,{csv_b64}" download="{filename}.csv">Download CSV</a>
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="{filename}.xlsx">Download Excel</a>
                <a href="data:application/pdf;base64,{pdf_b64}" download="{filename}.pdf">Download PDF</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

filtered_registrations = filtered_df[filtered_df['Source'] == 'Registrations']
filtered_transactions = filtered_df[filtered_df['Source'] == 'Transactions']
filtered_redemptions = filtered_df[filtered_df['Source'] == 'Redemptions']

# Ensure 'Date', 'Date', and 'Date' are in datetime format
registrations_df['Date'] = pd.to_datetime(registrations_df['Date'], errors='coerce')
transactions_df['Date'] = pd.to_datetime(transactions_df['Date'], errors='coerce')
redemptions_df['Date'] = pd.to_datetime(redemptions_df['Date'], errors='coerce')

# Drop rows with NaT in respective date columns
registrations_df = registrations_df.dropna(subset=['Date'], how='all')
transactions_df = transactions_df.dropna(subset=['Date'], how='all')
redemptions_df = redemptions_df.dropna(subset=['Date'], how='all')

# Extract month and year for each date type
registrations_df['RegMonth'] = registrations_df['Date'].dt.month
registrations_df['RegYear'] = registrations_df['Date'].dt.year
transactions_df['TransMonth'] = transactions_df['Date'].dt.month
transactions_df['TransYear'] = transactions_df['Date'].dt.year
redemptions_df['RedMonth'] = redemptions_df['Date'].dt.month
redemptions_df['RedYear'] = redemptions_df['Date'].dt.year

# Generate all months for the x-axis
all_months = pd.date_range(start=min(registrations_df['Date'].min(),
                                     transactions_df['Date'].min(),
                                     redemptions_df['Date'].min()),
                           end=max(registrations_df['Date'].max(),
                                   transactions_df['Date'].max(),
                                   redemptions_df['Date'].max()),
                           freq='MS').strftime('%b %Y')

# Group and count each category
registration = registrations_df.groupby(['RegYear', 'RegMonth'])['memberID'].count().reset_index(name='Registration')
transaction = transactions_df.groupby(['TransYear', 'TransMonth'])['transactionId'].count().reset_index(name='Transactions')
redemption = redemptions_df.groupby(['RedYear', 'RedMonth'])['orderID'].count().reset_index(name='Redemption')

registration['Month-Year'] = pd.to_datetime(registration['RegYear'].astype(str) + '-' + registration['RegMonth'].astype(str).str.zfill(2)).dt.strftime('%b %Y')
transaction['Month-Year'] = pd.to_datetime(transaction['TransYear'].astype(str) + '-' + transaction['TransMonth'].astype(str).str.zfill(2)).dt.strftime('%b %Y')
redemption['Month-Year'] = pd.to_datetime(redemption['RedYear'].astype(str) + '-' + redemption['RedMonth'].astype(str).str.zfill(2)).dt.strftime('%b %Y')


# Merge all data into one DataFrame
combined = pd.merge(pd.merge(registration[['Month-Year', 'Registration']],
                             transaction[['Month-Year', 'Transactions']],
                             on='Month-Year', how='outer'),
                    redemption[['Month-Year', 'Redemption']],
                    on='Month-Year', how='outer')

# Fill missing months with 0
def fill_missing_months(data, all_months):
    data = data.set_index('Month-Year')
    data = data.reindex(all_months, fill_value=0)
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Month-Year'}, inplace=True)
    return data

filled_combined = fill_missing_months(combined, all_months)

# Melt data for grouped bar chart
melted_data = filled_combined.melt(id_vars=['Month-Year'], var_name='Category', value_name='Count')

# Plot combined bar chart
fig1 = px.bar(
    melted_data,
    x='Month-Year',
    y='Count',
    color='Category',
    barmode='group',
    title="Monthly Registration, Transactions, and Redemption",
    color_discrete_map={
        'Registration': 'rgba(67, 148, 229, 0.6)',
        'Transactions': 'rgba(248, 174, 84, 0.6)',
        'Redemption': 'rgba(135, 111, 212, 0.6)', #lite purple
    },
    height=600 
)

# Update x-axis to make category labels horizontal
fig1.update_xaxes(
    type='category',
    tickangle=0,  # Ensure category labels are horizontal
    tickmode='array',  # Set the tick mode to ensure proper spacing
    title_text='Month-Year',  # Set the title for the x-axis (optional)
    title_standoff=10  # Space between title and axis
)

# Update layout if needed
fig1.update_layout(
    xaxis_title="Month-Year",  # Title for x-axis
    yaxis_title="Count",  # Title for y-axis
    legend_orientation='h',  # Set legend to horizontal
    legend=dict(
        x=1,   # Center the legend horizontally
        xanchor='right',  # Anchor legend to the center horizontally
        y=1.1,  # Position the legend above the chart
        yanchor='bottom',  # Anchor the legend to the bottom
    )
)

# Map Code below

# Prepare state data for registrations, transactions, and redemptions
states = registrations_df['State'].unique()
state_data = {}

for state in states:
    registrations = len(registrations_df[registrations_df['State'] == state])
    transactions = len(transactions_df[transactions_df['State'] == state])
    redemptions = len(redemptions_df[redemptions_df['State'] == state])
    state_data[state] = {
        "registrations": registrations,
        "transactions": transactions,
        "redemptions": redemptions
    }

# Prepare state data for OpenStreetMap visualization
states = registrations_df['State'].unique()
state_coords = {
    "Andhra Pradesh": [15.9129, 79.7400],
    "Arunachal Pradesh": [27.0972, 93.3617],
    "Assam": [26.2006, 92.9376],
    "Bihar": [25.0961, 85.3131],
    "Chhattisgarh": [21.2787, 81.8661],
    "Goa": [15.2993, 74.1240],
    "Gujarat": [22.2587, 71.1924],
    "Haryana": [29.0588, 76.0856],
    "Himachal Pradesh": [32.0598, 77.1734],
    "Jharkhand": [23.6102, 85.2799],
    "Karnataka": [12.9716, 77.5946],
    "Kerala": [10.8505, 76.2711],
    "Madhya Pradesh": [23.2599, 77.4126],
    "Maharashtra": [19.0760, 72.8777],
    "Manipur": [24.6637, 93.9063],
    "Meghalaya": [25.4670, 91.3662],
    "Mizoram": [23.1645, 92.9376],
    "Nagaland": [26.1584, 94.5624],
    "Odisha": [20.9517, 85.0985],
    "Punjab": [31.1471, 75.3412],
    "Rajasthan": [27.0238, 74.2179],
    "Sikkim": [27.5330, 88.6140],
    "Tamil Nadu": [13.0827, 80.2707],
    "Telangana": [17.1231, 79.2085],
    "Tripura": [23.9408, 91.9882],
    "Uttar Pradesh": [26.8467, 80.9462],
    "Uttarakhand": [30.0668, 79.0193],
    "West Bengal": [22.9868, 87.8550],
    "Andaman and Nicobar Islands": [11.7401, 92.6586],
    "Chandigarh": [30.7333, 76.7794],
    "Delhi": [28.6139, 77.2090],
    "Jammu and Kashmir": [33.7782, 76.5762],
}

# Prepare data for OpenStreetMap visualization
map_data = pd.DataFrame({
    "State": list(state_coords.keys()),
    "lat": [coord[0] for coord in state_coords.values()],  # Latitude
    "lon": [coord[1] for coord in state_coords.values()],  # Longitude
    "Registrations": [state_data[state]["registrations"] for state in state_coords],
    "Transactions": [state_data[state]["transactions"] for state in state_coords],
    "Redemptions": [state_data[state]["redemptions"] for state in state_coords],
})

fig2 = px.scatter_mapbox(
    map_data,
    lat="lat",  # Latitude column
    lon="lon",  # Longitude column
    hover_name="State",  # Display the state name in the tooltip
    hover_data={  # Customize hover data to include only the desired fields
        "Registrations": True,
        "Transactions": True,
        "Redemptions": True,
        "lat": False,  # Hide latitude
        "lon": False,  # Hide longitude
    },
    # size="Registrations",
    # size_max=30,
)

fig2.update_layout(
    mapbox_style="open-street-map",
    height=870,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    mapbox=dict(
        center=dict(lat=20.5937, lon=78.9629),  # Center of India
        zoom=1,  # Adjust zoom level for clarity
        bounds=dict(  # Set visible boundaries to India's extent
            west=68.0,  # Westernmost longitude of India
            east=97.0,  # Easternmost longitude of India
            south=6.5,  # Southernmost latitude of India
            north=37.5  # Northernmost latitude of India
        )
    )
)

col1, col2 = st.columns([3, 2])  # Adjust ratios for layout width

with col1:
    #Display chart
    
    st.markdown("<br>", unsafe_allow_html=True)
    if access_level == 1:  # Show download button only if access_level is 1

        download_button(filled_combined, "monthly_combined_report")
    st.plotly_chart(fig1, use_container_width=True, key='combined_fig')
    
    st.markdown(
    f"""
    <style>
        .overview-summary-container {{
            height: 270px;
            width: 100%;
            margin-top: -7px;
            overflow: hidden;
        }}
        .overview-summary-box {{
            text-align: justify; /* Justify the text */
        }}
        .overview-summary-value {{
            padding: 10px;
        }}
        .overview-summary-label {{
            font-size: 17px;
            color: #4A90E2;
            margin-bottom: 2px; /* Add spacing between points */
        }}
        .overview-summary-heading {{
            font-size: 20px;
            color: black;
            font-weight: bold;
            text-align: center; /* Center the heading */
            margin-bottom: 5px; /* Add spacing below the heading */
        }}
        .overview-summary-heading:hover {{
            color: #32CD32; /* Green color on hover */
        }}
    </style>
    <div class='overview-summary-container'>  
        <div class='overview-summary-box'>  
            <div class='overview-summary-value'>
                <div class='overview-summary-heading'>
                    Insight Summary
                </div>
                <div class='overview-summary-label'>
                    ⭐ The current redemption rates are low. Consider running targeted campaigns or offering discounts to encourage customer redemptions.
                </div>
                <div class='overview-summary-label'>
                    ⭐ The KYC completion rate is significantly below expectations. It's essential to ensure that customers complete their KYC process for better engagement.
                </div>
                <div class='overview-summary-label'>
                    ⭐ The point utilization rate is very low. To improve this, consider running targeted advertisements or promotional campaigns to encourage customers to redeem their points and increase engagement.
                </div>
            </div>     
        </div>  
    </div> 
    <div></div> 
    """,
    unsafe_allow_html=True
)


with col2:
    st.markdown("<br>", unsafe_allow_html=True)

    # Display map
    if access_level == 1:  # Show download button only if access_level is 1
        download_button(map_data, "map_data")
    st.plotly_chart(fig2, use_container_width=True)


col3, col4 = st.columns([2,2])

filtered_registrations['Quarter_Registration'] = filtered_registrations['Date'].dt.to_period('Q')
quarterly_registration = filtered_registrations.groupby(filtered_registrations['Quarter_Registration'])['memberID'].count().reset_index(name='Registration')
quarterly_registration['Quarter'] = quarterly_registration['Quarter_Registration'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")

# Calculate Quarterly Transactions
filtered_transactions['Quarter_Transaction'] = filtered_transactions['Date'].dt.to_period('Q')
quarterly_transactions = filtered_transactions.groupby(filtered_transactions['Quarter_Transaction'])['transactionId'].count().reset_index(name='Transactions')
quarterly_transactions['Quarter'] = quarterly_transactions['Quarter_Transaction'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")

# Calculate Quarterly Redemption
filtered_redemptions['Quarter_Redemption'] = filtered_redemptions['Date'].dt.to_period('Q')
quarterly_redemption = filtered_redemptions.groupby(filtered_redemptions['Quarter_Redemption'])['orderID'].count().reset_index(name='Redemption')
quarterly_redemption['Quarter'] = quarterly_redemption['Quarter_Redemption'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")

# Merge the dataframes on 'Quarter'
combined_df = pd.merge(quarterly_registration[['Quarter', 'Registration']], 
                       quarterly_transactions[['Quarter', 'Transactions']], on='Quarter', how='outer')
combined_df = pd.merge(combined_df, quarterly_redemption[['Quarter', 'Redemption']], on='Quarter', how='outer')

# Reshape the data for Plotly
combined_df_long = pd.melt(combined_df, id_vars=['Quarter'], value_vars=['Registration', 'Transactions', 'Redemption'], 
                           var_name='Category', value_name='Count')

# Create the combined bar chart
fig2 = px.bar(
    combined_df_long,
    x='Quarter',
    y='Count',
    color='Category',
    barmode='group',
    title="Quarterly Registration, Transactions, and Redemption",
    color_discrete_map={
        'Registration':  'rgba(67, 148, 229, 0.6)', 
        'Transactions':  'rgba(248, 174, 84, 0.6)',
        'Redemption':   'rgba(135, 111, 212, 0.6)',    # Light Orange
    }
)

fig2.update_layout(
    legend_orientation='h',  # Set legend to horizontal
    legend=dict(
        x=1,  # Center the legend horizontally
        xanchor='center',  # Anchor legend to the center horizontally
        y=1.1,  # Position the legend above the chart
        yanchor='bottom',  # Anchor the legend to the bottom
    )
)
# Update x-axis for category display
fig2.update_xaxes(type='category', title_text='Quarter', tickangle=0)

with col3:
# Display the combined chart and download button
    
    st.markdown("<br>", unsafe_allow_html=True)
    if access_level == 1:  # Show download button only if access_level is 1
        download_button(combined_df_long, "download-quarterly-report")  
    st.plotly_chart(fig2)

yearly_registration = filtered_registrations.groupby(filtered_registrations['Date'].dt.year)['memberID'].count().reset_index(name='Registration')
yearly_registration.columns = ['Year', 'Registration']

# Yearly transactions data
yearly_transactions = filtered_transactions.groupby(filtered_transactions['Date'].dt.year)['transactionId'].count().reset_index(name='Transactions')
yearly_transactions.columns = ['Year', 'Transactions']

# Yearly redemption data
yearly_redemption = filtered_redemptions.groupby(filtered_redemptions['Date'].dt.year)['orderID'].count().reset_index(name='Redemption')
yearly_redemption.columns = ['Year', 'Redemption']

# Merging all three DataFrames based on 'Year'
combined_data = yearly_registration.merge(yearly_transactions, on='Year', how='outer')
combined_data = combined_data.merge(yearly_redemption, on='Year', how='outer')

combined_data_year = pd.melt(combined_data, id_vars=['Year'], value_vars=['Registration', 'Transactions', 'Redemption'], 
                           var_name='Category', value_name='Count')

# Create a bar chart with the combined data
fig3 = px.bar(
    combined_data_year,
    x='Year',
    y='Count',
    color='Category',
    title="Yearly Registration, Transactions, and Redemption",
    color_discrete_map={
        'Registration':  'rgba(67, 148, 229, 0.6)', 
        'Transactions':  'rgba(248, 174, 84, 0.6)',
        'Redemption':   'rgba(135, 111, 212, 0.6)',
    },
    barmode='group'  
)
fig3.update_xaxes(type='category', title_text='Quarter', tickangle=0)

fig3.update_layout(
    legend_orientation='h',  # Set legend to horizontal
    legend=dict(
        x=1.5,  # Center the legend horizontally
        xanchor='right',  # Anchor legend to the center horizontally
        y=1.1,  # Position the legend above the chart
        yanchor='bottom',  # Anchor the legend to the bottom
    )
)
# Show the chart and provide a download button
with col4:
    
    st.markdown("<br>", unsafe_allow_html=True)
    if access_level == 1:  # Show download button only if access_level is 1
        download_button(combined_data, "download-yearly-report")
    st.plotly_chart(fig3, use_container_width=True)