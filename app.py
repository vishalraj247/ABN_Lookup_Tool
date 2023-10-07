import streamlit as st
import pandas as pd
import os
import io

from keywordgen import generate_business_name_suggestions
from abnlookup import query_postcodes

def reset_session_state():
    st.session_state.initial_suggestions = None
    st.session_state.refined_names = None
    st.session_state.combined_suggestions = None
    st.session_state.result_df = None

if 'initial_suggestions' not in st.session_state:
    st.session_state.initial_suggestions = None

if 'refined_names' not in st.session_state:
    st.session_state.refined_names = None

if 'combined_suggestions' not in st.session_state:
    st.session_state.combined_suggestions = None

if 'result_df' not in st.session_state:
    st.session_state.result_df = None

if 'industry_input' not in st.session_state:
    st.session_state.industry_input = ""

if 'postcode_input' not in st.session_state:
    st.session_state.postcode_input = ""

if 'allow_edit_initial' not in st.session_state:
    st.session_state.allow_edit_initial = False

if 'allow_edit_refined' not in st.session_state:
    st.session_state.allow_edit_refined = False

if 'allow_edit_combined' not in st.session_state:
    st.session_state.allow_edit_combined = False

st.set_page_config(page_title="ABN Lookup Tool", page_icon="🔍", layout='wide', initial_sidebar_state="expanded")
st.title("ABN Lookup Tool")

sidebar = st.sidebar
sidebar.title("Navigation")
page = sidebar.radio("Select a Page", ["Home", "Contact Us", "Feedback"])

if page == "Home":
    sidebar.header("User Input Features")
    st.session_state.industry_input = sidebar.text_input("Enter Industry:", value=st.session_state.industry_input)
    st.session_state.postcode_input = sidebar.text_input("Enter Postcode:", value=st.session_state.postcode_input, max_chars=4)

    if sidebar.button("Generate Suggestions"):
        reset_session_state()
        additional_names = ["Bugz Off", "Sydney Side Pest", "Pest Control", "Pesticides"]
        with st.spinner('Generating Business Names...'):
            initial_suggestions, refined_names, combined_suggestions = generate_business_name_suggestions(st.session_state.industry_input, additional_names)
            while not initial_suggestions:
                st.warning("No initial suggestions generated. Regenerating...")
                initial_suggestions, refined_names, combined_suggestions = generate_business_name_suggestions(st.session_state.industry_input, additional_names)
            st.session_state.initial_suggestions = initial_suggestions
            st.session_state.refined_names = refined_names
            st.session_state.combined_suggestions = combined_suggestions

    if st.session_state.initial_suggestions:
        st.subheader(f"Initial suggested Names for {st.session_state.industry_input} Industry:")
        st.session_state.allow_edit_initial = st.radio(
            "Edit Initial Suggested Names?",
            [True, False],
            key="edit_initial",
            index=int(not st.session_state.allow_edit_initial)
        )
        if st.session_state.allow_edit_initial:
            edited_initial_suggestions = st.text_area("Edit Initial Suggested Names:", ', '.join(st.session_state.initial_suggestions))
            st.session_state.initial_suggestions = edited_initial_suggestions.split(', ')
        else:
            st.write(f"Initial Suggestions: {', '.join(st.session_state.initial_suggestions)}")

    if st.session_state.refined_names:
        st.subheader(f"Refined Names for {st.session_state.industry_input} Industry:")
        st.session_state.allow_edit_refined = st.radio(
            "Edit Refined Names?",
            [True, False],
            key="edit_refined",
            index=int(not st.session_state.allow_edit_refined)
        )
        if st.session_state.allow_edit_refined:
            edited_refined_names = st.text_area("Edit Refined Names:", ', '.join(st.session_state.refined_names))
            st.session_state.refined_names = edited_refined_names.split(', ')
        else:
            st.write(f"Refined Names: {', '.join(st.session_state.refined_names)}")

    if st.session_state.combined_suggestions:
        st.subheader(f"Combined Suggestions for {st.session_state.industry_input} Industry:")
        st.session_state.allow_edit_combined = st.radio(
            "Edit Combined Suggestions?",
            [True, False],
            key="edit_combined",
            index=int(not st.session_state.allow_edit_combined)
        )
        if st.session_state.allow_edit_combined:
            edited_combined_suggestions = st.text_area("Edit Combined Suggestions:", ', '.join(st.session_state.combined_suggestions))
            st.session_state.combined_suggestions = edited_combined_suggestions.split(', ')
        else:
            st.write(f"Combined Suggestions: {', '.join(st.session_state.combined_suggestions)}")


        if st.button("Explore Businesses Now"):
            with st.spinner('Fetching Business Information...'):
                postcodes_to_query = {st.session_state.postcode_input}
                st.session_state.result_df = query_postcodes(postcodes_to_query, st.session_state.combined_suggestions)

    if st.session_state.result_df is not None and not st.session_state.result_df.empty:
        st.subheader(f"Businesses in {st.session_state.postcode_input} related to {st.session_state.industry_input}:")

        # Search bar for ABN or Business Name
        search_term = st.text_input("Search ABN or Business Name:")
        if search_term:
            # Filter the DataFrame based on the search term
            mask = (st.session_state.result_df['ABN'].astype(str).str.contains(search_term)) | \
                (st.session_state.result_df['Organisation Name'].str.contains(search_term, case=False))
            display_df = st.session_state.result_df[mask]
        else:
            display_df = st.session_state.result_df

        # Display the (filtered) DataFrame
        st.write('Result DataFrame:', display_df)

        # Buttons to download DataFrame as CSV or Excel
        csv = display_df.to_csv(index=False)
        # Convert the CSV string to bytes
        csv_bytes = csv.encode('utf-8')
        # Create a bytes buffer
        csv_buffer = io.BytesIO(csv_bytes)

        if 'csv_download_clicked' not in st.session_state:
            st.session_state.csv_download_clicked = False

        if st.download_button('Download CSV', data=csv_buffer, file_name='result_data.csv', mime='text/csv'):
            st.session_state.csv_download_clicked = True

        if st.session_state.csv_download_clicked:
            st.success('CSV Download started!')
            st.session_state.csv_download_clicked = False  # Reset the state after showing the message

        # Convert the DataFrame to Excel and get the Excel file's bytes
        excel_bytes = io.BytesIO()
        with pd.ExcelWriter(excel_bytes, engine='xlsxwriter') as writer:
            display_df.to_excel(writer, sheet_name='Sheet1', index=False)
        excel_bytes.seek(0)

        if 'excel_download_clicked' not in st.session_state:
            st.session_state.xlsx_download_clicked = False

        if st.download_button('Download Excel', data=excel_bytes, file_name='result_data.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
            st.session_state.xlsx_download_clicked = True

        if st.session_state.xlsx_download_clicked:
            st.success('Excel Download started!')
            st.session_state.xlsx_download_clicked = False  # Reset the state after showing the message

elif page == "Contact Us":
    st.write(
        """
        ## Contact Us
        
        If you have any questions, suggestions, or feedback, please feel free to reach out to us at:
        
        - Name: WorkSafe Wizards
        - Email: vishal.raj@student.uts.edu.au
        - Address: UTS, Broadway
        
        We look forward to hearing from you!
        """
    )

elif page == "Feedback":
    st.write("## Feedback Form")
    name = st.text_input("Your Name")
    feedback = st.text_area("Please provide your feedback:")
    if st.button("Submit Feedback"):
        feedback_data = {'Name': [name], 'Feedback': [feedback]}
        feedback_df = pd.DataFrame(feedback_data)
        
        if os.path.isfile('feedback.csv'):
            existing_feedback_df = pd.read_csv('feedback.csv', index_col=0)
            updated_feedback_df = pd.concat([existing_feedback_df, feedback_df], ignore_index=True)
        else:
            updated_feedback_df = feedback_df
        
        updated_feedback_df.to_csv('feedback.csv')
        st.success(f"Thank you for your feedback, {name}!")

# Styling: Add some style to the layout using Markdown
st.markdown(
    """
<style>
    .reportview-container {
        background-color: #F0F2F6
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)