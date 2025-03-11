import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def reset_Session():
    st.session_state.clear()


def Data_Type_Conversion():
    for col in st.session_state.Manipulated_dtype:
        Latest_Manipulated_dtype_col = st.session_state[f"datatype_{col}"]  # Get the latest selected value

        # Apply conversion to the stored dataframe
        if Latest_Manipulated_dtype_col == "STRING":
            st.session_state.Manipulated_data[col] = st.session_state.Manipulated_data[col].astype(str)
            st.session_state.Manipulated_dtype[col] = "STRING"
        elif Latest_Manipulated_dtype_col == "INT64":
            st.session_state.Manipulated_data[col] = pd.to_numeric(st.session_state.Manipulated_data[col], errors='coerce').round().astype('Int64')
            st.session_state.Manipulated_dtype[col] = "INT64"
        elif Latest_Manipulated_dtype_col == "FLOAT64":
            st.session_state.Manipulated_data[col] = pd.to_numeric(st.session_state.Manipulated_data[col], errors='coerce').astype('float64')
            st.session_state.Manipulated_dtype[col] = "FLOAT64"
        elif Latest_Manipulated_dtype_col == "BOOLEAN":
            st.session_state.Manipulated_data[col] = st.session_state.Manipulated_data[col].astype(bool)
            st.session_state.Manipulated_dtype[col] = "BOOLEAN"
        elif Latest_Manipulated_dtype_col == "DATETIME64":
            st.session_state.Manipulated_data[col] = pd.to_datetime(st.session_state.Manipulated_data[col], errors='coerce')
            st.session_state.Manipulated_dtype[col] = "DATETIME64"


#------------------------------------------------------------------------------------------------------#
#------------------------------------------- UPLOAD FRESH FILE-----------------------------------------#
#------------------------------------------------------------------------------------------------------#
uploaded_file = st.file_uploader("Upload Your csv File",'csv',on_change=reset_Session)

if uploaded_file is not None:

    #----- Raw Data Store -----#
    if "Raw_data" not in st.session_state:
        st.session_state.Raw_data = pd.read_csv(uploaded_file)
        st.session_state.Raw_data = st.session_state.Raw_data.convert_dtypes()
        st.session_state.Raw_dtypes = {col: str(dtype).upper() for col, dtype in st.session_state.Raw_data.dtypes.items()}

    Raw_data = st.session_state.Raw_data
    st.write("### Raw Data Preview")
    st.write(f"Number of records: {len(Raw_data)}")
    st.write(Raw_data)

    #---- Manipulated Data ----#
    if "Manipulated_data" not in st.session_state:
        st.session_state.Manipulated_data = st.session_state.Raw_data.copy()
        st.session_state.Manipulated_dtype = {col: str(dtype).upper() for col, dtype in st.session_state.Manipulated_data.dtypes.items()}

    st.write("### Manipulated Data Preview")

    manipulated_data_counts_placeholder = st.empty()
    manipulated_data_placeholder = st.empty()

    def update_ui():
        manipulated_data_counts_placeholder.write(f"**Number of records:** {len(st.session_state.Manipulated_data)}")
        manipulated_data_placeholder.dataframe(st.session_state.Manipulated_data)

    update_ui()

#----------------------------------------------Define SideBar------------------------------------------#
    st.sidebar.header("Data Cleaning")

    if st.sidebar.button("Reset"):
        st.session_state.Manipulated_data = st.session_state.Raw_data.copy()
        update_ui()
    
    if st.sidebar.button("Drop NA"):
        st.session_state.Manipulated_data = st.session_state.Manipulated_data.dropna().copy()
        update_ui()

    if st.sidebar.button("Fill with Mean"):
        temp_df=st.session_state.Manipulated_data.copy()
        int_col_store=[]
        for col in temp_df.select_dtypes(include=["int64"]).columns:
            int_col_store.append(col)
            temp_df[col]=temp_df[col].astype("float64")
        temp_df=temp_df.fillna(temp_df.mean(numeric_only=True))
        for i in int_col_store:
            temp_df[i]=temp_df[i].astype("int64")
        st.session_state.Manipulated_data = temp_df.copy()
        update_ui()

    if st.sidebar.button("Fill with Median"):
        temp_df_meadian=st.session_state.Manipulated_data.copy()
        int_col_store_median=[]
        for col in temp_df_meadian.select_dtypes(include=["int64"]).columns:
            int_col_store_median.append(col)
            temp_df_meadian[col]=temp_df_meadian[col].astype("float64")
        temp_df_meadian=temp_df_meadian.fillna(temp_df_meadian.median(numeric_only=True))
        for i in int_col_store_median:
            temp_df_meadian[i]=temp_df_meadian[i].astype("int64")
        st.session_state.Manipulated_data = temp_df_meadian.copy()
        update_ui()

    if st.sidebar.button("Fill with Mode"):
        st.session_state.Manipulated_data = st.session_state.Manipulated_data.fillna(st.session_state.Manipulated_data.mode().iloc[0])
        update_ui()

    if st.sidebar.button("Remove Duplicates"):
        st.session_state.Manipulated_data = st.session_state.Manipulated_data.drop_duplicates()
        update_ui()


    with st.sidebar.expander("Convert Data Type"):
        for i in list(st.session_state.Manipulated_data.columns):
            col1, col2 =st.columns(2)
            
            with col1:
                st.text(i)

            with col2:
                st.selectbox(
                    label='Datatype',
                    options=['STRING', 'INT64', 'FLOAT64', 'BOOLEAN', 'DATETIME64'],
                    key=f"datatype_{i}",  # Unique key per column
                    index=['STRING', 'INT64', 'FLOAT64', 'BOOLEAN', 'DATETIME64'].index(st.session_state.Manipulated_dtype[i]),
                    on_change=Data_Type_Conversion
                )

#---------------------------------------------------------------------------------------------------#
# Exploratory Data View

    st.subheader("📊 Exploratory Data Analysis")
    st.write("#### Basic Statistics")
    st.write(st.session_state.Manipulated_data.describe())

#  Correlation Heatmap
    st.write("#### Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(st.session_state.Manipulated_data.select_dtypes(include=['number']).corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    
# Value Counts for Categorical Columns
    st.write("#### Categorical value counts")
    categorical_columns = st.session_state.Manipulated_data.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
    if categorical_columns:
        selected_column=st.selectbox("Select a categorical Column!",categorical_columns)
        st.write(st.session_state.Manipulated_data[selected_column].value_counts())

# Data Visualization Categorical Data Bar Chart
    st.write("#### Categorical Data Bar Chart")
    if categorical_columns:
        selected_column_bar=st.selectbox("Select a Categorical Column",categorical_columns)
        fig,ax=plt.subplots()
        st.session_state.Manipulated_data[selected_column_bar].value_counts().plot(kind='bar',ax=ax)
        st.pyplot(fig)

# Data Visualization Line plot of Trends
    date_columns = st.session_state.Manipulated_data.select_dtypes(include=['datetime64']).columns.tolist()
    if date_columns:
        selected_date_column = st.selectbox("Select a date column for trend analysis", date_columns)
        numeric_columns = st.session_state.Manipulated_data.select_dtypes(include=['number']).columns.tolist()
        if numeric_columns:
            selected_numeric_column = st.selectbox("Select a numeric column for trend analysis", numeric_columns)
            fig, ax = plt.subplots()
            st.session_state.Manipulated_data.groupby(selected_date_column)[selected_numeric_column].mean().plot(kind='line', ax=ax)
            st.pyplot(fig)

# Data Visualization Categorical Data Bar Chart
    st.write("#### Histogram for Numerical Distribution")
    numeric_columns_all= st.session_state.Manipulated_data.select_dtypes(include=['number']).columns.tolist()
    if numeric_columns_all:
        selected_column_bar=st.selectbox("Select a Categorical Column",numeric_columns_all)
        fig,ax=plt.subplots()
        st.session_state.Manipulated_data[selected_column_bar].plot(kind='hist',ax=ax)
        st.pyplot(fig)