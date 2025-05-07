import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
import os

access_level = int(os.getenv("ACCESS_LEVEL", "0"))  # Default to "0" if not set

st.set_page_config(page_title="Registration Dashboard", layout="wide")

# Load external CSS
with open("C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\style.css") as f:
    custom_css = f.read()

st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv('C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Registrations_Sample.csv')

# Load Data
df = load_data()

# Download Filtered Data (Dynamic for Each Chart)
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


col1, col2 = st.columns([1,2])
with col1:
    # Total Registrations
    total_registrations = len(filtered_df)
    
    # Today's Total Registrations
    registrations_on_date = len(filtered_df[filtered_df["Date"].dt.date == pd.Timestamp.today().date()])
    
    # Silver and Gold Members
    silver_members = len(filtered_df[filtered_df["memberTier"] == "Silver"])
    gold_members = len(filtered_df[filtered_df["memberTier"] == "Gold"])
    
    # Completed KYC
    completed_kyc = len(filtered_df[filtered_df["KYCStatus"] == 1])

    # Streamlit Insights Display
    summary_html = f"""  
    <div class='summary-container' style="height: 620px; width: 100;">  
        <div class='summary-box'>  
            <div class='summary-value'>Insight Summary
                <div class='summary-label' style="font-size: 20px; text-align: justify;">1. <b>🔢 Total Registrations:</b><br> The total number of registrations is <b>{total_registrations}</b> members.</div>  
                <div class='summary-label' style="font-size: 20px; text-align: justify;">2. <b>📅 Today's Total Registration:</b><br> The number of registrations completed today is <b>{registrations_on_date}</b> members.</div>  
                <div class='summary-label' style="font-size: 20px; text-align: justify;">3. <b>⭐ Silver Members:</b><br> There are <b>{silver_members}</b> members registered as Silver Members.</div>  
                <div class='summary-label' style="font-size: 20px; text-align: justify;">4. <b>🏅 Gold Members:</b><br> The total number of Gold Members is <b>{gold_members}</b>.</div>  
                <div class='summary-label' style="font-size: 20px; text-align: justify;">5. <b>📋 Completed KYC:</b><br> The number of members who have completed their KYC is <b>{completed_kyc}</b>.</div>  
            </div>      
        </div>  
    </div>  """ 
    st.markdown(summary_html, unsafe_allow_html=True)




# Ensure 'Date' is in datetime format and handle invalid dates
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

    # Group by Year and Month, and calculate Registration count
    monthly_registration = filtered_df.groupby(['Year', 'Month'])['memberID'].count().reset_index(name='Registration')

    # Create 'Month-Year' column for plotting or display
    monthly_registration['Month-Year'] = pd.to_datetime(
        monthly_registration['Year'].astype(str) + '-' + monthly_registration['Month'].astype(str).str.zfill(2)
    ).dt.strftime('%b %Y')

    # Verify column names after modification
    print(monthly_registration.columns)
else:
    # Handle the case when there are no valid dates available
    all_months = []
    monthly_registration = pd.DataFrame()  # Empty DataFrame or handle as needed
    print("No valid date data available.")

# Ensure all months are represented
def fill_missing_months(data, all_months):
    data = data.set_index('Month-Year')
    data = data.reindex(all_months, fill_value=0)
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Month-Year'}, inplace=True)
    return data

# Now, ensure that you're using the correct column names and checking for empty DataFrame
if not monthly_registration.empty:
    filled_monthly = fill_missing_months(monthly_registration[['Month-Year', 'Registration']], all_months)
else:
    print("monthly_registration DataFrame is empty.")
    filled_monthly = pd.DataFrame()  # Handle the empty case

# Proceed with plotting if data exists
if not filled_monthly.empty:
    fig1 = px.bar(
        filled_monthly,
        x='Month-Year',
        y='Registration',
        title="Monthly Registration",
        color_continuous_scale=['#4394E5','#876FD4','#C7C7C7','#F8AE54']
    )
    fig1.update_xaxes(type='category')

    with col2:
        # Score Cards with Individual Boxes and 3D Effect
        st.markdown(
        f"""
        <div class='metric-container' style="display: flex; flex-wrap: nowrap; justify-content: space-between; gap: 10px; width: 100%;">
            <div class='metric-box' style="flex: 1 1 calc(20% - 10px); text-align: center;">
                <div class='metric-value'>{format_number(filtered_df['memberID'].nunique())}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Total Members</div>
            </div>
            <div class='metric-box' style="flex: 1 1 calc(20% - 10px); text-align: center;">
                <div class='metric-value'>{format_number(filtered_df[filtered_df['memberStatus'] == 'Active'].shape[0])}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Active Members</div>
            </div>
            <div class='metric-box' style="flex: 1 1 calc(20% - 10px); text-align: center;">
                <div class='metric-value'>{format_number(filtered_df[filtered_df['KYCStatus'] == 1].shape[0])}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Pending KYC</div>
            </div>
            <div class='metric-box' style="flex: 1 1 calc(20% - 10px); text-align: center;">
                <div class='metric-value'>{format_number(len(filtered_df) - len(filtered_df.drop_duplicates(subset=['memberID'])))}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Duplicate Registrations</div>
            </div>
            <div class='metric-box' style="flex: 1 1 calc(20% - 10px); text-align: center;">
                <div class='metric-value'>{format_number(len(filtered_df.drop_duplicates(subset=['memberID'])))}</div>
                <div class='metric-label' style="font-size: 18px; font-weight: bold;" >Unique Registrations</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
        if access_level == 1:
            download_button(filled_monthly, "download-monthly-report")
        st.plotly_chart(fig1, use_container_width=True, key='fig1')
else:
    print("No data to display for monthly Registration.")



col3, col4 = st.columns([2,2])

# Quaterly Chart
filtered_df['Quarter'] = filtered_df['Date'].dt.to_period('Q')
quarterly_registration = filtered_df.groupby(filtered_df['Date'].dt.to_period('Q'))['memberID'].count().reset_index(name='Registration')

# Format Quarter for display
quarterly_registration['Quarter'] = quarterly_registration['Date'].apply(lambda x: f"{x.start_time.strftime('%b')}-{x.end_time.strftime('%b')} {x.start_time.year}")
# Plot the chart
fig2 = px.bar(
    quarterly_registration,
    x='Quarter',
    y='Registration',  # Ensure this matches the column name in the DataFrame
    title="Quarterly Registration",
    color_discrete_sequence=['#AFDC8F', '#92C5F9', '#F8AE54','#B6A6E9']
)
fig2.update_xaxes(type='category')

# Display the chart and download button
with col3:  
    if access_level == 1:  
        download_button(quarterly_registration, "download-quarterly-report")
    st.plotly_chart(fig2)

# Yearly Chart
yearly_registration = filtered_df.groupby(filtered_df['Date'].dt.year)['memberID'].count().reset_index(name='Registration')
yearly_registration.columns = ['Year', 'Registration']

# Pie chart instead of line chart
fig3 = px.pie(
    yearly_registration,
    names='Year',
    values='Registration',
    title="Yearly Registration Distribution",
    color='Year',
    color_discrete_sequence=['#a2d2ff']
)
fig3.update_traces(textinfo='percent+label')
with col4:
    if access_level == 1:
        download_button(yearly_registration, "download-yearly-report")
    st.plotly_chart(fig3)

col5, col6 = st.columns([2,2])
total_registered = len(filtered_df)  # Total members in the dataset
active_members = len(filtered_df[filtered_df['memberStatus'] == 'Active'])  # Active members

# Creating a DataFrame for the comparison
comparison_data = pd.DataFrame({
    'memberStatus': ['Total Registered', 'Active Members'],
    'count': [total_registered, active_members]
})

# Plotting the comparison bar chart
fig_comparison = px.bar(
    comparison_data, x='memberStatus', y='count', 
    title='Total Registered vs Active Members', text='count', 
    color='memberStatus', color_discrete_sequence=['#F8AE54', '#B6A6E9']
)
with col5:
    if access_level == 1:
        download_button(comparison_data, "total_vs_active_members_comparison")
    st.plotly_chart(fig_comparison, use_container_width=True)

# Grouping by memberStatus to show count of active and inactive members
member_status = filtered_df['memberStatus'].value_counts().reset_index(name='count')
member_status.columns = ['memberStatus', 'count']  # Rename columns for clarity

# Plotting the bar chart for Active vs Inactive Members
fig_member_status = px.bar(
    member_status, x='memberStatus', y='count', 
    title='Active vs Inactive Members', text='count', 
    color='memberStatus', color_discrete_sequence=['#AFDC8F', '#B6A6E9']
)

# Display the chart in Streamlit
with col6:
    if access_level == 1:
        download_button(member_status, "active_vs_inactive_members")
    st.plotly_chart(fig_member_status, use_container_width=True)

col7, col8 = st.columns([2,2])
# Filter for pending KYC
kyc_pending = filtered_df[filtered_df['KYCStatus'] == 0]

# Count pending KYC by MemberType
kyc_status_count = kyc_pending['MemberType'].value_counts().reset_index()
kyc_status_count.columns = ['MemberType', 'count']

# Sort by count in descending order and select top 4
kyc_status_count = kyc_status_count.sort_values(by='count', ascending=False).head(4)

# Create the bar chart
fig6 = px.bar(
    kyc_status_count, 
    x='MemberType', 
    y='count', 
    title='Pending KYC Status by Member Type (Top 4)', 
    text='count', 
    color_discrete_sequence=['#F8AE54']
)

# Add download button and display the chart
with col7:
    if access_level == 1:  # Show download button only if access_level is 1
        download_button(kyc_status_count, "kyc_pending_count")
    st.plotly_chart(fig6, use_container_width=True)


member_tier_count = filtered_df['memberTier'].value_counts().reset_index()
member_tier_count.columns = ['memberTier', 'count']
fig5 = px.bar(
    member_tier_count, x='memberTier', y='count', 
    title='Count by Member Tier', text='count', color_discrete_sequence=['#876FD4']
)
with col8:
    if access_level == 1:  # Show download button only if access_level is 1
        download_button(member_tier_count, "member_tier_count")
    st.plotly_chart(fig5, use_container_width=True)