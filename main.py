from flask import Flask, render_template
import io
import pandas as pd
import hvplot.pandas
import holoviews as hv
import panel as pn
from bokeh.sampledata.iris import flowers

# Initialize Flask app
app = Flask(__name__)

# Initialize Panel extensions
pn.extension(sizing_mode="stretch_width")
hv.extension("bokeh")

accent_color = "#ff286e"

# Selection linker for cross-filtering
selection_linker = hv.selection.link_selections.instance()

# Create scatter and histogram plots
def create_scatter_hist():
    scatter_plot = flowers.hvplot.scatter(
        x="sepal_length", y="sepal_width", c=accent_color, responsive=True, height=350
    ).opts(size=10, tools=["hover"], active_tools=["box_select"])

    hist_plot = flowers.hvplot.hist(
        "petal_width", c=accent_color, responsive=True, height=350
    ).opts(tools=["hover"], active_tools=["box_select"])

    scatter_linked = selection_linker(scatter_plot)
    hist_linked = selection_linker(hist_plot)
    return scatter_linked, hist_linked

scatter, hist = create_scatter_hist()

# Create Panel widgets for filtering
sepal_length_slider = pn.widgets.FloatSlider(
    name='Sepal Length', 
    start=flowers['sepal_length'].min(), 
    end=flowers['sepal_length'].max(), 
    value=flowers['sepal_length'].min(), 
    step=0.1
)

sepal_width_slider = pn.widgets.FloatSlider(
    name='Sepal Width', 
    start=flowers['sepal_width'].min(), 
    end=flowers['sepal_width'].max(), 
    value=flowers['sepal_width'].min(), 
    step=0.1
)

# Apply filters based on widget values
def filter_data(sepal_length, sepal_width):
    filtered_flowers = flowers[ 
        (flowers['sepal_length'] >= sepal_length) &
        (flowers['sepal_width'] >= sepal_width)
    ]
    return filtered_flowers

# Link filters to update plots
@pn.depends(sepal_length=sepal_length_slider, sepal_width=sepal_width_slider)
def update_plots(sepal_length, sepal_width):
    filtered_data = filter_data(sepal_length, sepal_width)
    scatter_filtered = filtered_data.hvplot.scatter(
        x="sepal_length", y="sepal_width", c=accent_color, responsive=True, height=350
    ).opts(size=10, tools=["hover"], active_tools=["box_select"])

    hist_filtered = filtered_data.hvplot.hist(
        "petal_width", c=accent_color, responsive=True, height=350
    ).opts(tools=["hover"], active_tools=["box_select"])

    scatter_filtered = selection_linker(scatter_filtered)
    hist_filtered = selection_linker(hist_filtered)

    return pn.Column(scatter_filtered, hist_filtered)

# Reset Button Functionality
reset_button = pn.widgets.Button(name="Reset Filters", button_type="warning", width=150)

def reset_filters(event):
    # Reset slider values
    sepal_length_slider.value = sepal_length_slider.start
    sepal_width_slider.value = sepal_width_slider.start
    
    # Clear chart-based selections
    selection_linker.selection = None  # Properly clear the box selection
    
    # Reinitialize plots
    global scatter, hist
    scatter, hist = create_scatter_hist()
    
    # Force the update of the layout
    layout[1].objects = [scatter, hist]

reset_button.on_click(reset_filters)

# Function to convert DataFrame to CSV using StringIO
def convert_to_csv(df):
    csv = df.to_csv(index=False)
    return io.StringIO(csv)

# Function to convert DataFrame to Excel using BytesIO
def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Create download buttons
csv_download = pn.widgets.FileDownload(
    filename='filtered_data.csv',
    button_type='primary',
    callback=lambda: convert_to_csv(filter_data(sepal_length_slider.value, sepal_width_slider.value)),
    label='Download CSV'
)

excel_download = pn.widgets.FileDownload(
    filename='filtered_data.xlsx',
    button_type='primary',
    callback=lambda: convert_to_excel(filter_data(sepal_length_slider.value, sepal_width_slider.value)),
    label='Download Excel'
)

# Layout with the download buttons, filter options, and reset button
layout = pn.Column(
    pn.Row(csv_download, excel_download, reset_button),  # Reset button included
    update_plots
)

# Create Panel template with filters
dashboard = pn.template.FastListTemplate(
    title="Dashboard",
    header_background=accent_color,
    main=[sepal_length_slider, sepal_width_slider, layout],
)

# Serve the Panel app using a separate route
@app.route("/dashboard")
def serve_dashboard():
    return dashboard.servable()

# Serve the Flask app
@app.route("/")
def index():
    return (
        "<h1>Welcome to the Dashboard</h1>"
        "<p>Visit the <a href='/dashboard'>Dashboard</a>.</p>"
    )

if __name__ == "__main__":
    pn.serve({'/dashboard': dashboard}, port=5000, show=False)
