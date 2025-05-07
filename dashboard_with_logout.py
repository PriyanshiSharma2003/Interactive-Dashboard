from flask import Flask, render_template, request, redirect, session, url_for
import csv
import subprocess
import time
import os
import panel as pn
from threading import Thread
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psutil
import pymysql
from pymysql.cursors import DictCursor  # Import DictCursor for dictionary-like results

app = Flask(__name__)
app.secret_key = "your_secret_key"

# # Function to read user credentials from the CSV file
# def read_users_from_csv(file_path='Accesslevel.csv'):
#     users = {}
#     if not os.path.exists(file_path):
#         return users

#     with open(file_path, mode='r', newline='', encoding='utf-8') as file:
#         csv_reader = csv.DictReader(file)
#         for row in csv_reader:
#             email = row['email']
#             password = row['password']
#             access_Level = row['accessLevel']  # Use the correct column name
#             users[email] = {'password': password, 'access_Level': int(access_Level)}  # Ensure access_Level is an integer
#     return users

# # Function to authenticate user using the CSV data
# def authenticate_user(email, password):
#     users = read_users_from_csv()
#     if email in users:
#         if users[email]['password'] == password:
#             return users[email]['access_Level']
#     return None

# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = pymysql.connect(
            host="localhost",  # Replace with your MySQL host
            user="root",       # Replace with your MySQL username
            password="tiger",  # Replace with your MySQL password
            database="access_table"  # Replace with your database name
        )
        return connection
    except pymysql.connect.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Function to read user credentials from the MySQL database
def read_users_from_db():
    users = {}
    connection = connect_to_database()
    if not connection:
        return users

    try:
        cursor = connection.cursor(DictCursor) 
        query = "SELECT email, password, access_level FROM access"  # Replace with your table name
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            email = row['email']
            password = row['password']
            access_level = row['access_level']  # Ensure this matches the column name in your table
            users[email] = {'password': password, 'access_Level': int(access_level)}

        cursor.close()
        connection.close()
        return users
    except pymysql.Error as err:
        print(f"Error reading from MySQL: {err}")
        return users

# Function to authenticate user using the database data
def authenticate_user(email, password):
    users = read_users_from_db()
    if email in users:
        if users[email]['password'] == password:
            return users[email]['access_Level']
    return None

streamlit_processes = []

def kill_streamlit_processes():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if it's a Streamlit process
            if 'streamlit' in proc.info['name'].lower() or \
               (proc.info['cmdline'] and 'streamlit' in ' '.join(proc.info['cmdline']).lower()):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Clear the stored processes list
    streamlit_processes.clear()

# Function to start Streamlit apps at the specified file paths (in a separate thread)
def start_streamlit_app(file_path, port, access_Level):
    try:
        env = {**os.environ, "ACCESS_LEVEL": str(access_Level)}
        process = subprocess.Popen(
            ['streamlit', 'run', file_path, '--server.port', str(port), '--server.headless=True'],
            env=env
        )
        streamlit_processes.append(process)
        time.sleep(2)
    except Exception as e:
        print(f"Error starting app {file_path} on port {port}: {e}")

@app.route('/logout')
def logout():
    kill_streamlit_processes()  # Kill all Streamlit processes
    session.clear()  # Clear session data
    return redirect(url_for('login_page'))


# Function to create the Panel layout with Tabs for Member Dashboard
def create_member_dashboard():
    if 'access_Level' not in session:
        return redirect(url_for('login_page'))

    access_Level = session.get('access_Level')

    # Paths to the Streamlit apps
    overview_path = "C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Overview.py"
    registrations_path = "C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Registration.py"
    trans_path = "C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Transaction.py"
    reedemptions_path = "C:\\Users\\priya\\OneDrive\\Desktop\\Office\\Python Dashboard\\Dashboard\\codes\\Redemption.py"

    # Start the Streamlit apps in different threads
    Thread(target=start_streamlit_app, args=(overview_path, 8513, access_Level)).start()
    Thread(target=start_streamlit_app, args=(registrations_path, 8502, access_Level)).start()
    Thread(target=start_streamlit_app, args=(trans_path, 8503, access_Level)).start()
    Thread(target=start_streamlit_app, args=(reedemptions_path, 8504, access_Level)).start()

    # Welcome message
    welcome_message = pn.pane.Markdown("# Welcome to Panasonic Samriddhi", sizing_mode='stretch_width')

    # Create logout button with JavaScript to call the Flask logout route
    logout_button = pn.widgets.Button(
        name="Logout",
        button_type="danger",
        width=100,
        margin=(-5, 0, 5, 10)  # top, right, bottom, left margins
    )
    
    # Create a JavaScript callback for the logout button
    logout_js = """
    <script>
    function logout() {
        window.location.href = '/logout';
    }
    </script>
    """
    
    # Attach the JavaScript callback to the button
    logout_button.js_on_click(args={}, code="logout()")

    # Create tabs
    tabs = pn.Tabs(
        ("Overview", pn.pane.HTML(f'<iframe src="http://localhost:8513" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        ("Registration", pn.pane.HTML(f'<iframe src="http://localhost:8502" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        ("Transaction", pn.pane.HTML(f'<iframe src="http://localhost:8503" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        ("Redemption", pn.pane.HTML(f'<iframe src="http://localhost:8504" height="100%" width="100%" frameborder="0" style="border:none; height:100vh; width:100vw;"></iframe>')),
        sizing_mode='stretch_width'
    )

    # Wrap tabs in a Column to control its size
    tabs_column = pn.Column(
        tabs,
        sizing_mode='stretch_width',
        width_policy='max'
    )

    # Create a row with tabs and logout button
    header_row = pn.Row(
        tabs_column,
        logout_button,
        sizing_mode='stretch_width',
        max_width=2000  # Prevent excessive width
    )

    # Create the main layout
    layout = pn.Column(
        welcome_message,
        header_row,
        sizing_mode='stretch_both',
        max_width=2000  # Prevent excessive width
    )

    # Add the JavaScript to the layout
    layout.append(pn.pane.HTML(logout_js))

    # Save Panel layout as HTML file
    html_file_path = "member_dashboard.html"
    layout.save(html_file_path, embed=True)

    # Read the content of the saved HTML file and return it as a string
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return html_content


@app.route('/')
def login_page():
    return render_template('login.html')


def send_password_reset_email(email, username):
    def send_email():
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "gangpriyanshi@gmail.com"
        password = "kiwa ywae liyv tebk"
        admin_email = "priyanshi62577@gmail.com"

        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login(sender_email, password)
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = admin_email
                message["Subject"] = "Password Reset Request"
                body = f"Hi Admin,\n\nUser {username} ({email}) has requested a password reset."
                message.attach(MIMEText(body, "plain"))
                server.sendmail(sender_email, admin_email, message.as_string())
                print(f"Password reset request sent to Admin")
        except Exception as e:
            print(f"Failed to send email: {e}")

    Thread(target=send_email).start()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Login attempt: Email={email}, Password={password}")  # Debug form inputs

        access_Level = authenticate_user(email, password)
        print(f"Login Access Level: {access_Level}")

        if access_Level is not None:
            session['email'] = email
            session['access_Level'] = access_Level
            print(f"Session set: {session}")  # Debug session variables

            return redirect(url_for('member_dashboard'))

        else:
            print("Invalid credentials")  # Debug failure
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']  # Capture the username

        # Query the database for the user
        users = read_users_from_db()

        if email in users:
            # Send the email with the username and email in the body
            send_password_reset_email(email, username)
            return render_template('forgot_password.html', message="Password reset email sent successfully!")
        else:
            return render_template('forgot_password.html', error="Email not found")

    return render_template('forgot_password.html')
# @app.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email']
#         username = request.form['username']  # Capture the username
#         users = read_users_from_csv()
#         if email in users:
#             # Send the email with the username and email in the body
#             send_password_reset_email(email, username)
#             return render_template('forgot_password.html', message="Password reset email sent successfully!")
#         else:
#             return render_template('forgot_password.html', error="Email not found")
#     return render_template('forgot_password.html')

# Flask route for the Member dashboard
@app.route('/member-dashboard')
def member_dashboard():
    print(f"Session in member_dashboard: {session}")  # Debug session access

    if 'access_Level' not in session:
        print("Access level missing in session, redirecting to login.")
        return redirect(url_for('login'))
    
    return create_member_dashboard()

if __name__ == '__main__':
    app.run()
