import streamlit as st
import pandas as pd
import plotly.express as px

# Title of the dashboard
st.title("Dashboard for Data Filtering and Visualization")

# Step 1: File Upload
st.sidebar.header("Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Load the uploaded Excel file into a Pandas DataFrame
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File uploaded successfully!")
        
        # Display the first few rows of the dataset
        st.subheader("Preview of the Uploaded Data")
        df = df[[df.columns.to_list()[0], df.columns.to_list()[1], df.columns.to_list()[3]]]
        st.write(df.describe())
        st.subheader("Number of Services")
        st.write(len(df))
        st.subheader("Number of Accredited Labs")
        st.write(len(df['ID'].unique()))
        st.subheader("Number of Standards")
        st.write(len(df['Standard'].value_counts()))
        
        # Step 2: Filter Options
        st.sidebar.header("Filter Options")
        
        # Multi-select for 'Material_Product_Tested'
        material_options = list(df['Material_Product_Tested'].unique())
        selected_materials = st.sidebar.multiselect(
            "Select Material/Product Tested", 
            options=material_options, 
            default=material_options
        )
        
        # Dropdown for selecting 'Standard'
        standard_options = ["All"] + list(df['Standard'].unique())
        selected_standard = st.sidebar.selectbox(
            "Select Standard Specifications/Techniques", 
            options=standard_options
        )
        
        # Slider for selecting the number of top standards to display
        top_n = st.sidebar.slider(
            "Select Number of Top Standards to Display",
            min_value=5,  # Minimum number of standards to display
            max_value=50,  # Maximum number of standards to display
            value=10,  # Default value
            step=1  # Step size
        )
        
        # Filter the DataFrame based on user selections
        filtered_df = df.copy()
        if selected_materials:
            filtered_df = filtered_df[filtered_df['Material_Product_Tested'].isin(selected_materials)]
        if selected_standard != "All":
            filtered_df = filtered_df[filtered_df['Standard'] == selected_standard]
        
        # Display the filtered data
        st.subheader("Filtered Data")
        st.write(filtered_df)
        
        # Step 3: Data Visualization with Plotly
        st.header("Data Visualization")
        
        # Calculate total occurrences for percentage calculation
        total_occurrences = df['Material_Product_Tested'].value_counts().sum()  # Total occurrences in the dataset
        
        # Bar Chart: Count of Unique IDs by Material_Product_Tested
        st.subheader("Bar Chart: Count of Unique IDs by Material/Product Tested")
        material_id_counts = (
            filtered_df.groupby('Material_Product_Tested')['ID']
            .nunique()
            .reset_index()
            .rename(columns={'ID': 'Count of Unique IDs'})
        )
        fig_bar = px.bar(
            material_id_counts,
            x='Material_Product_Tested',
            y='Count of Unique IDs',
            title="Count of Unique IDs by Material/Product Tested",
            labels={'Material_Product_Tested': 'Material/Product', 'Count of Unique IDs': 'Number of Unique IDs'}
        )
        st.plotly_chart(fig_bar)
        
        # Pie Chart: Distribution of Tests Across Materials/Products
        st.subheader("Pie Chart: Distribution of Tests Across Materials/Products")
        material_counts = filtered_df['Material_Product_Tested'].value_counts().reset_index()
        material_counts.columns = ['Material_Product_Tested', 'Count']
        fig_pie = px.pie(
            material_counts,
            names='Material_Product_Tested',
            values='Count',
            title="Distribution of Tests Across Materials/Products"
        )
        st.plotly_chart(fig_pie)
        
        # New: Bar Plot for Material_Product_Tested Occurrences
        st.subheader("Bar Chart: Material/Product Tested Occurrences")
        material_occurrences = filtered_df['Material_Product_Tested'].value_counts().reset_index()
        material_occurrences.columns = ['Material_Product_Tested', 'Occurrences']
        
        # Calculate the percentage of occurrences for the selected material(s)
        filtered_total_occurrences = material_occurrences['Occurrences'].sum()  # Total occurrences in filtered data
        filtered_percentage = (filtered_total_occurrences / total_occurrences) * 100  # Percentage of filtered data
        
        # Update the title to include the total percentage (styled in red)
        title_with_red_percentage = (
            f"Occurrences of Material/Product Tested "
            f"(<span style='color:red;'>{filtered_percentage:.2f}%</span> of Total)"
        )
        
        fig_material_occurrences = px.bar(
            material_occurrences,
            x='Material_Product_Tested',
            y='Occurrences',
            title=title_with_red_percentage,
            labels={'Material_Product_Tested': 'Material/Product', 'Occurrences': 'Count'},
            color_discrete_sequence=["#1f77b4"],  # Blue color for bars
            text_auto=True  # Display count values on top of bars
        )
        fig_material_occurrences.update_xaxes(tickangle=45)  # Rotate x-axis labels for better readability
        st.plotly_chart(fig_material_occurrences)
        
        # New: Bar Plot for Standard Occurrences
        st.subheader("Bar Chart: Standard Occurrences")
        standard_occurrences = filtered_df['Standard'].value_counts().reset_index()
        standard_occurrences.columns = ['Standard', 'Occurrences']
        fig_standard_occurrences = px.bar(
            standard_occurrences,
            x='Standard',
            y='Occurrences',
            title="Occurrences of Standard",
            labels={'Standard': 'Standard', 'Occurrences': 'Count'}
        )
        fig_standard_occurrences.update_xaxes(tickangle=45)
        st.plotly_chart(fig_standard_occurrences)
        
        # New: Bar Plot for Top-N Standards with Percentage Statistics
        st.subheader(f"Bar Chart: Top {top_n} Standards by Frequency")
        total_occurrences = standard_occurrences['Occurrences'].sum()  # Total occurrences of all standards
        top_n_standards = standard_occurrences.head(top_n)  # Select top N standards
        top_n_total_occurrences = top_n_standards['Occurrences'].sum()  # Total occurrences of top N standards
        top_n_percentage = (top_n_total_occurrences / total_occurrences) * 100  # Percentage of top N standards
        
        # Style the top N and percentage values
        styled_top_n = f"<span style='color:green;'>{top_n}</span>"
        styled_percentage = f"<span style='color:red;'>{top_n_percentage:.2f}%</span>"
        
        # Display the percentage statistic with styled text
        st.markdown(
            f"The top {styled_top_n} standards account for {styled_percentage} of all standard occurrences.",
            unsafe_allow_html=True
        )
        
        # Create the bar plot for top N standards
        fig_top_n_standards = px.bar(
            top_n_standards,
            x='Standard',
            y='Occurrences',
            title=f"Top {top_n} Standards by Frequency",
            labels={'Standard': 'Standard', 'Occurrences': 'Count'},
            color_discrete_sequence=["#1f77b4"],  # Blue color for bars
            text_auto=True  # Display count values on top of bars
        )
        fig_top_n_standards.update_xaxes(tickangle=45)  # Rotate x-axis labels for better readability
        fig_top_n_standards.update_layout(
            bargap=0.2,  # Adjust gap between bars
            font=dict(size=12)  # Font size for better visibility
        )
        st.plotly_chart(fig_top_n_standards)
        
    except Exception as e:
        st.error(f"Error loading or processing the file: {e}")
else:
    st.info("Please upload an Excel file to get started.")