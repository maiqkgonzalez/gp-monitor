import streamlit as st
from config_reader import get_firewalls, read_config
from datetime import date, timedelta
from db_reader import get_users_overtime, get_max_users_per_firewall
import pandas as pd

st.set_page_config(page_title="GP-Monitor", page_icon="🌎")

# Read config.yaml
config_file = read_config()
firewalls = get_firewalls(config_file)

# Extract firewall names for the filter
firewall_filter = []
for firewall in firewalls:
    firewall_filter.append(firewall["name"])

# App title
st.title("GP-Monitor 🌎")

# Sidebar filter configuration
st.sidebar.subheader("Filters")

# Firewall filter
selected_firewall = st.sidebar.multiselect(
    label="Firewalls", options=firewall_filter, default=firewall_filter
)

# Time filter
selected_time = st.sidebar.selectbox(
    label="Time range",
    options=["last day", "last 7 days", "last 30 days", "custom"],
)

if selected_time == "custom":
    start_date = st.sidebar.date_input(label="Start", value=date.today())
    end_date = st.sidebar.date_input(label="End", value=date.today())
elif selected_time == "last day":
    start_date = date.today() - timedelta(days=1)
    end_date = date.today()
elif selected_time == "last 7 days":
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()
elif selected_time == "last 30 days":
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()

# Validate at least one firewall is selected
if selected_firewall == []:
    st.warning("Please select at least one firewall.")
    st.stop()

# Convert dates to string format for the query
start_date_str = start_date.strftime("%Y-%m-%d 00:00:00")
end_date_str = end_date.strftime("%Y-%m-%d 23:59:59")

# --- Users over time chart ---
st.subheader("Users over time")

# Fetch data from DB
users_over_time_data = get_users_overtime(
    selected_firewall, start_date_str, end_date_str
)

# Convert list of tuples to DataFrame
dataframe = pd.DataFrame(
    users_over_time_data, columns=["timestamp", "firewall", "users"]
)

# Convert timestamp column from string to datetime
dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])

# Round timestamps to 10-minute intervals to align records across firewalls
dataframe["timestamp"] = dataframe["timestamp"].dt.floor("10min")

# Pivot table: one column per firewall, aggregate duplicates with mean
dataframe_pivot = dataframe.pivot_table(
    index="timestamp", columns="firewall", values="users", aggfunc="mean"
)

# Render line chart
st.line_chart(data=dataframe_pivot)

# --- Max users table ---
st.subheader("Max Users")

# Fetch max users per firewall from DB
max_users_data = get_max_users_per_firewall(selected_firewall)

# Convert to DataFrame and render table
dataframe_max = pd.DataFrame(max_users_data, columns=["Firewall", "Max Users"])
st.dataframe(dataframe_max, hide_index=True)
