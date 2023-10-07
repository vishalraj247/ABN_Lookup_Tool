import streamlit as st
from keywordgen import generate_business_name_suggestions
from abnlookup import query_postcodes

industry_input = 'Pest Control'
postcode_input = '2000'

st.title('ABN Lookup Tool')

# Debugging directly in Streamlit
suggested_names = generate_business_name_suggestions(industry_input)
#suggested_names = [name.split('. ')[1] for name in suggested_names if '. ' in name]

st.write('Suggested Names:', suggested_names)
print(suggested_names)

result_df = query_postcodes(postcode_input, suggested_names)
st.write('Result DataFrame:', result_df)

'''import streamlit as st
import pandas as pd
import os

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

st.set_page_config(page_title="ABN Lookup Tool", page_icon="🔍", layout='wide', initial_sidebar_state="expanded")

st.title("ABN Lookup Tool")

sidebar = st.sidebar
sidebar.title("Navigation")
page = sidebar.radio("Select a Page", ["Home", "Contact Us", "Feedback"])

if page == "Home":
    st.sidebar.header("User Input Features")
    st.session_state.industry_input = st.sidebar.text_input("Enter Industry:", value=st.session_state.industry_input)
    st.session_state.postcode_input = st.sidebar.text_input("Enter Postcode:", value=st.session_state.postcode_input, max_chars=4)

    if st.sidebar.button("Generate Suggestions"):
        reset_session_state()
        additional_names = ["Bugz Off", "Sydney Side Pest", "Pest Control", "Pesticides"]  # Example additional names
        # Including a spinner here for user feedback during processing
        with st.spinner('Generating Business Names...'):
            initial_suggestions, refined_names, combined_suggestions = generate_business_name_suggestions(st.session_state.industry_input, additional_names)
            # Adding a warning and regeneration loop in case no suggestions are returned
            while not initial_suggestions:
                st.warning("No initial suggestions generated. Regenerating...")
                initial_suggestions, refined_names, combined_suggestions = generate_business_name_suggestions(st.session_state.industry_input, additional_names)
            st.session_state.initial_suggestions = initial_suggestions
            st.session_state.refined_names = refined_names
            st.session_state.combined_suggestions = combined_suggestions

    if st.session_state.initial_suggestions:
        st.subheader(f"Initial suggested Names for {st.session_state.industry_input} Industry:")
        edited_initial_suggestions = st.text_area("Edit Initial Suggested Names:", ', '.join(st.session_state.initial_suggestions))
        st.session_state.initial_suggestions = edited_initial_suggestions.split(', ')

    if st.session_state.refined_names:
        st.subheader(f"Refined Names for {st.session_state.industry_input} Industry:")
        edited_refined_names = st.text_area("Edit Refined Names:", ', '.join(st.session_state.refined_names))
        st.session_state.refined_names = edited_refined_names.split(', ')

    if st.session_state.combined_suggestions:
        st.subheader(f"Combined Suggestions for {st.session_state.industry_input} Industry:")
        edited_combined_suggestions = st.text_area("Edit Combined Suggestions:", ', '.join(st.session_state.combined_suggestions))
        st.session_state.combined_suggestions = edited_combined_suggestions.split(', ')

        if st.button("Explore Businesses Now"):
            with st.spinner('Fetching Business Information...'):
                postcodes_to_query = {st.session_state.postcode_input}
                st.session_state.result_df = query_postcodes(postcodes_to_query, st.session_state.combined_suggestions)

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
)'''