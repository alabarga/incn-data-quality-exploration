import streamlit as st
import yaml
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Function to display metadata as a table
def display_metadata(metadata):
    st.write("### Metadata Summary")
    metadata_df = pd.DataFrame(list(metadata.items()), columns=["Key", "Value"])
    st.table(metadata_df)

# Function to display excluded records as a table
def display_excluded_records(records):
    st.write("### Excluded Records")
    excluded_records = []
    for record in records:
        excluded_records.append({
            'Name': record.get('name', 'N/A'),
            'Status': record.get('status', 'N/A'),
            'Values': record.get('values', 'N/A')
        })
    excluded_df = pd.DataFrame(excluded_records)
    st.table(excluded_df)

# Function to display field details
def display_field_details(field_name, field_data):
    # Display the field name and status with a colored bullet
    status = field_data.get('status', 'UNKNOWN')
    bullet_color = '🟢' if status == 'PASS' else '🔴' if status == 'FAIL' else '⚪'
    st.write(f"{bullet_color} **{field_name}** - Status: {status}")

    # Prepare data for table display
    results = field_data.get('results', [])
    table_data = []
    for result in results:
        table_data.append({
            'Name': result.get('name', 'N/A'),
            'Status': result.get('status', 'N/A'),
            'Records Checked': result.get('records checked', 'N/A'),
            'Invalid Values': result.get('invalid values', 'N/A')
        })

    # Display the table
    if table_data:
        st.table(table_data)

# Function to display summary of FAIL tests with details
def display_fail_summary(data):
    st.write("### Summary of FAIL Tests")
    fail_tests = []

    for key, value in data.items():
        if isinstance(value, dict):
            for field_name, field_data in value.items():
                if field_data.get('status') == 'FAIL':
                    for result in field_data.get('results', []):
                        if result.get('status') == 'FAIL':
                            fail_tests.append({
                                'Field': field_name,
                                'Test Name': result.get('name', 'N/A'),
                                'Status': result.get('status', 'N/A'),
                                'Records Checked': result.get('records checked', 'N/A'),
                                'Invalid Values': result.get('invalid values', 'N/A')
                            })

    if fail_tests:
        fail_df = pd.DataFrame(fail_tests)
        st.table(fail_df)
    else:
        st.write("No FAIL tests found.")


# Function to display plausibility data
def display_plausibility(plausibility_data):
    selected_name = st.selectbox("Select a Plausibility Test", [d['name'] for d in plausibility_data])

    selected_data = next((d for d in plausibility_data if d['name'] == selected_name), None)
    if selected_data:
        st.write(f"### {selected_name} Details")

        summary_data = {key: value for key, value in selected_data.items() if key != 'values'}
        st.write(summary_data)

        values = selected_data.get('values')
        if values:
            if isinstance(values, list):
                # Display histogram
                st.write("#### Values Histogram")
                sns.histplot(values, kde=True)
                st.pyplot(plt)
            elif isinstance(values, dict):
                keys = list(values.keys())
                if all(isinstance(k, dict) for k in values.values()):
                    # Barchart for years with sub-dict
                    st.write("#### Yearly Data Barchart")
                    years = keys
                    means = [sum(k * v for k, v in year_dict.items()) / sum(year_dict.values()) for year_dict in values.values()]
                    
                    sns.barplot(x=years, y=means)
                    st.pyplot(plt)
                else:
                    # Barchart for keys and values
                    st.write("#### Values Barchart")
                    sns.barplot(x=list(values.keys()), y=list(values.values()))
                    st.pyplot(plt)

# File uploader
uploaded_file = st.file_uploader("Upload a YAML file", type="yml")

if uploaded_file:
    # Load the YAML file
    data = yaml.safe_load(uploaded_file)

    # Sidebar for first level entries
    st.sidebar.title("Explore Data")
    menu_options = list(data.keys())
    selected_menu = st.sidebar.selectbox("Select Category", menu_options)

    # Main section
    if selected_menu:
        selected_data = data[selected_menu]

        if selected_menu == 'metadata':
            display_metadata(selected_data)
        elif selected_menu == 'excluded records':
            display_excluded_records(selected_data)
        elif selected_menu == 'completeness & conformance (single field)':
            # Use tabs for second level entries
            tab_names = list(selected_data.keys())
            tabs = st.tabs(["Summary"] + tab_names)
            
            with tabs[0]:
                display_fail_summary(selected_data)
            
            for i, tab_name in enumerate(tab_names):
                with tabs[i+1]:
                    sub_data = selected_data[tab_name]
                    if isinstance(sub_data, dict):
                        # Searchable selector for fields inside
                        field_names = list(sub_data.keys())
                        selected_field = st.selectbox(f"Select a field in {tab_name}", field_names)
                        if selected_field:
                            field_data = sub_data[selected_field]
                            display_field_details(selected_field, field_data)
                    else:
                        st.write(f"No detailed data available for {tab_name}.")
        elif selected_menu == 'plausibility':
            display_plausibility(selected_data.get('descriptive statistics', []))
        else:
            st.write(f"No detailed data available for {selected_menu}.")
else:
    st.write("Please upload a YAML file to explore the data.")
