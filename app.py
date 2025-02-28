import streamlit as st
from google.cloud import storage
from io import BytesIO
import os
import requests
import json
import pandas as pd
import time
import streamlit_extras
from streamlit_extras.switch_page_button import switch_page

# Set your GCP credentials C:\Users\kartikeys\Desktop\listdemo\servicecert-relevate-dev-403605-991ce9234fb2.json
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "\Demo\servicecert-relevate-dev-403605-991ce9234fb2.json"

# Define the relative path to the service account file

# relative_path = "relevate-dev-403605-3d2cdf274874.json"

# Get the absolute path dynamically
credentials_path = os.path.join(os.getcwd(), relative_path)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "\servicecert-relevate-dev-403605-991ce9234fb2.json"
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

# Load secrets from Streamlit cloud
gcp_credentials = st.secrets["gcp_service_account"]

# Convert secrets to JSON format
service_account_json = json.dumps(gcp_credentials)

# Set up authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/service_account.json"

# Save JSON file temporarily (Streamlit Cloud does not allow direct env vars for GCP)
with open("/tmp/service_account.json", "w") as f:
    f.write(service_account_json)

# Initialize Google Cloud Storage client
client = storage.Client()

# GCS bucket name
BUCKET_NAME = "relevate-dev-403605-list"

file_path = "list/123456/TestFORDemo_27_2_25/"  # Folder path
# file_path = "list/123456/test1/"  # Folder path

uuid = "99570796-f508-11ef-972f-42004e494300"

#BUCKET_NAME = "gs://relevate-dev-403605-list/list/123456/TestFORDemo_27_2_25"
# fileName = "gs://relevate-dev-403605-list/list/123456/TestFORDemo_27_2_25/"
fileName = f"gs://{BUCKET_NAME}/{file_path}"

def upload_to_gcs(bucket_name, file):
    # client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path + file.name)
    blob.upload_from_file(file, content_type="text/csv")
    return f"File {file.name} uploaded successfully to {bucket_name}"



def fetch_data(uuid, fileName):
    """Function to call the API and fetch data."""
    url = f"https://getdatavaultstatus-580005102993.us-central1.run.app/?uuid={uuid}&fileName={fileName}"
    print(url)  # Replace with actual API URL
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # Assuming the API returns JSON data
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None



data_list = []

if "page" not in st.session_state:
    st.session_state.page = "home"

# First Page
if st.session_state.page == "home":
    # Streamlit UI

    st.title("Upload CSV to GCS")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file:
        # Initialize session state for uploaded file URL
        if "file_url" not in st.session_state:
            st.session_state.file_url = None

        if st.button("Upload to GCS"):
            st.session_state.file_url = upload_to_gcs(BUCKET_NAME, uploaded_file)
            st.success("File uploaded successfully!")
        fileName = fileName + uploaded_file.name

    # Show new button only after upload success
    if st.session_state.get("file_url"):
        if st.button("File Upload Details"):
            placeholder = st.empty()
            while True:
                data = fetch_data(uuid, fileName)
                if data and "results" in data:
                    if data["results"] == 'No records found':
                        # Create a DataFrame with a message
                        df = pd.DataFrame([{"Filename": f"{uploaded_file.name}", "Status": "No records found"}])
                        placeholder.dataframe(df)  # Display DataFrame
                        # break  # Stop the loop immediately
                        
                    else:
                        # for result in data["results"]:
                        #     print(result)
                        #     data_entry = {
                        #         "Filename": result.get("filename", "N/A"),
                        #         "Status": result.get("status", "N/A"),
                        #     }
                        #     data_list.append(data_entry)
                        
                        data_list = [{
                            "Filename": result.get("filename", "N/A"),
                            "Status": result.get("status", "N/A"),
                        } for result in data["results"]]
                
                        df = pd.DataFrame(data_list)
                
                        # Update the table with the latest data
                        placeholder.dataframe(df)
                
                        #Check if status is 'GoldenKeyDataExportCompleted'
                        # if any(result.get("status") == "GoldenKeyDataExportCompleted" for result in data["results"]):
                        #     # st.success("Process completed! Stopping API calls.")
                        #     break

                        #Check if status is 'GoldenKeyDataExportCompleted' or 'Failed'
                        if any(result.get("status") in {"GoldenKeyDataExportCompleted", "Failed"} for result in data["results"]):
                            break

            
                    # time.sleep(300)  # Wait for 5 minutes before the next call
                    time.sleep(120)  # Wait for 5 minutes before the next call

    # Create a hyperlink-like button to navigate
    if st.button("Report"):
        st.session_state.page = "second"
        st.rerun()

# Second Page
elif st.session_state.page == "second":
    st.title("Appended Demographic")

    # Option to go back
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown(
    f'<iframe title="EntityResolutionData" width="1000" height="500" src="https://app.powerbi.com/view?r=eyJrIjoiMjE0ODY5MmYtMDE4MS00Y2E1LTg4ZTAtODI0OWQyOGEyYzRjIiwidCI6IjFmMmI1ZGU5LWU5ZGQtNDE5YS1hZGU1LWZlZTZjOTJlN2Y5MiIsImMiOjN9" frameborder="0" allowFullScreen="true"></iframe>',
    unsafe_allow_html=True
    )
