import streamlit as st
import pandas as pd
import os

# Assuming you have these modules and functions
from keywordgen import generate_business_name_suggestions
from abnlookup import query_postcodes

def reset_session_state():
    st.session_state.suggested_names = None
    st.session_state.result_df = None

# Set default values in the session state if they don't exist
if 'suggested_names' not in st.session_state:
    st.session_state.suggested_names = None

if 'result_df' not in st.session_state:
    st.session_state.result_df = None

if 'industry_input' not in st.session_state:
    st.session_state.industry_input = ""

if 'postcode_input' not in st.session_state:
    st.session_state.postcode_input = ""

# Set page config
st.set_page_config(page_title="ABN Lookup Tool", page_icon="🔍", layout='wide', initial_sidebar_state="expanded")

# Title of the app
st.title("ABN Lookup Tool")

# Add a sidebar
sidebar = st.sidebar
sidebar.title("Navigation")
page = sidebar.radio("Select a Page", ["Home", "Contact Us", "Feedback"])

# Content of pages
if page == "Home":
    st.sidebar.header("User Input Features")
    user_industry_input = st.sidebar.text_input("Enter Industry:", value=st.session_state.industry_input)
    user_postcode_input = st.sidebar.text_input("Enter Postcode:", value=st.session_state.postcode_input, max_chars=4)

    if st.sidebar.button("Generate Suggestions"):
        if user_industry_input and user_postcode_input:
            reset_session_state()
            st.session_state.industry_input = user_industry_input
            st.session_state.postcode_input = user_postcode_input
            
            with st.spinner('Generating Business Names...'):
                st.session_state.suggested_names = generate_business_name_suggestions(st.session_state.industry_input)
                while not st.session_state.suggested_names:
                    st.warning("No suggestions generated. Regenerating...")
                    st.session_state.suggested_names = generate_business_name_suggestions(st.session_state.industry_input)

    if st.session_state.suggested_names:
        st.subheader(f"Suggested Names for {st.session_state.industry_input} Industry:")
        edited_suggested_names = st.text_area("Edit Suggested Names:", ', '.join(st.session_state.suggested_names))
        st.session_state.suggested_names = edited_suggested_names.split(', ')

        if st.button("Explore Businesses Now"):
            with st.spinner('Fetching Business Information...'):
                postcodes_to_query = {st.session_state.postcode_input}
                st.session_state.result_df = query_postcodes(postcodes_to_query, st.session_state.suggested_names)

    if st.session_state.result_df is not None and not st.session_state.result_df.empty:
        st.subheader(f"Businesses in {st.session_state.postcode_input} related to {st.session_state.industry_input}:")
        st.write('Result DataFrame:', st.session_state.result_df)

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