import streamlit as st
from streamlit_plotly_events import plotly_events
import pandas as pd
import plotly.express as px
import os
import warnings
from streamlit.runtime.caching import cache_data

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Python Statistics Dashboard-Humidity",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title(" :bar_chart: Python Statistics Dashboard_Humidity_NMCC_SASO")
st.markdown("<style>div.block-container{padding-top:2rem;} </style>", unsafe_allow_html=True)

# File uploader
fl = st.file_uploader(" :file_folder: Please upload a file", type=(["csv", "xlsx", "xls", "txt"]))

@cache_data
def read_file(uploaded_file):
    if uploaded_file is None:
        return None
    file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
    try:
        if file_extension in [".csv", ".txt"]:
            return pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        elif file_extension in [".xlsx", ".xls"]:
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format")
            return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

if fl is not None:
    st.subheader("Data Clean / Imputations")
    filename = fl.name
    st.write("Uploaded file:", filename)
    df = read_file(fl)

    if df is None:
        st.error("Failed to load data. Please check the file format and try again.")
    else:
        # Data cleaning
        df = df.drop([0, 2, 3, 4], errors='ignore')
        df.columns = [f"{str(a)} {b}".strip() for a, b in zip(df.iloc[0], df.iloc[1])]
        df = df.drop([1, 5], errors='ignore')
        df = df.drop('nan Time', axis=1, errors='ignore')
        datetime_col = df.columns[0]
        df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')

        # Extract date and time
        df['date'] = df[datetime_col].dt.date
        df['time'] = df[datetime_col].dt.time
        df = df.drop(datetime_col, axis=1)
        columns = ['date', 'time'] + [col for col in df.columns if col not in ['date', 'time']]
        df = df[columns]

        # Create datetime column for plotting
        df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))

        # Convert numeric columns (except datetime)
        colms = df.columns.to_list()[2:-1]  # Exclude date, time, datetime
        df[colms] = df[colms].apply(pd.to_numeric, errors='coerce')

        # Sidebar filters
        url = "https://th.bing.com/th/id/R.2d3c79b1699019e964f4e82b2a40c81c?rik=PIZK9MUpT6aZcQ&riu=http%3a%2f%2fwww.saudireadymix.com%2fwp-content%2fuploads%2f2018%2f07%2fsaso-logo-300x225.png&ehk=vWN6vnN03wlp59myw0uCfEzncMhz%2b8zcT79y1oxsl2s%3d&risl=&pid=ImgRaw&r=0"
        st.sidebar.image(url, width="stretch")
        st.sidebar.header("Filter Data")
        start_date = st.sidebar.date_input("Start date", df['date'].min())
        end_date = st.sidebar.date_input("End date", df['date'].max())
        start_time = st.sidebar.time_input("Start time", pd.Timestamp('00:00:00').time())
        end_time = st.sidebar.time_input("End time", pd.Timestamp('23:59:59').time())

        # Filter dataframe
        mask = (
            (df['date'] >= start_date) & 
            (df['date'] <= end_date) & 
            (df['time'] >= start_time) & 
            (df['time'] <= end_time)
        )
        filtered_df = df.loc[mask]

        st.write("Filtered Data Preview:")
        st.write(filtered_df.head(5))

        # -----------------------------
        # Humidity Figures Only
        # -----------------------------
        hum_cols = [col for col in filtered_df.columns if 'Humidity' in col]

        # Humidity Plot (Figure 1)
        st.subheader("💧 Humidity Sensors Visualization")
        if hum_cols:
            hum_fig = px.line(
                filtered_df,
                x='datetime',
                y=hum_cols,
                title='Humidity Sensors',
                labels={'value': 'Humidity'},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            hum_fig.update_layout(dragmode='select')
            st.plotly_chart(hum_fig, width="stretch")

            # Capture selection events
            selected_points = plotly_events(hum_fig, select_event=True)

            # Filter data based on selected points
            if selected_points:
                selected_indices = [point['pointIndex'] for point in selected_points]
                filtered_hum_df = filtered_df.iloc[selected_indices]
            else:
                filtered_hum_df = filtered_df  # Use full dataset if no selection

            # Humidity Statistics (Figure 3)
            st.subheader("📊 Humidity Statistics")
            for sensor in hum_cols:
                with st.expander(f"{sensor} Statistics"):
                    sensor_data = filtered_hum_df[sensor].dropna()
                    if not sensor_data.empty:
                        stats = {
                            "Count": len(sensor_data),
                            "Max": sensor_data.max(),
                            "Min": sensor_data.min(),
                            "Mean": sensor_data.mean(),
                            "Median": sensor_data.median(),
                            "Mode": mode(sensor_data.astype(int)),
                            "Std": sensor_data.std(),
                            "Std/Count": sensor_data.std() / len(sensor_data)
                        }
                    else:
                        stats = {k: None for k in ["Count","Max","Min","Mean","Median","Mode","Std","Std/Count"]}
                    stats_df = pd.DataFrame(list(stats.items()), columns=["Metric", "Value"])
                    st.table(stats_df)
        else:
            st.warning("No humidity columns found")
else:
    st.warning("Please upload a file to proceed.")
