import streamlit as st
import pandas as pd
import os
import io

from keywordgen import generate_business_name_suggestions, refine_business_names, combine_and_deduplicate
from abnlookup import query_postcodes
from webscrapping import get_all_business_names

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

if 'scraped_names' not in st.session_state:
    st.session_state.scraped_names = None

if 'industry_input' not in st.session_state:
    st.session_state.industry_input = ""

if 'postcode_input' not in st.session_state:
    st.session_state.postcode_input = ""

if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

if 'allow_edit_initial' not in st.session_state:
    st.session_state.allow_edit_initial = False

if 'allow_edit_refined' not in st.session_state:
    st.session_state.allow_edit_refined = False

if 'allow_edit_combined' not in st.session_state:
    st.session_state.allow_edit_combined = False

if 'explore_businesses' not in st.session_state:
    st.session_state.explore_businesses = False

st.set_page_config(page_title="ABN Lookup Tool", page_icon="🔍", layout='wide', initial_sidebar_state="expanded")
# Using containers for better layout
header_container = st.container()
content_container = st.container()

# Adding content to containers
with header_container:
    st.title("ABN Lookup Tool")
    #st.image("your_logo.png", width=100)  # Add your logo if available

sidebar = st.sidebar
sidebar.title("Navigation")
page = sidebar.radio("Select a Page", ["Home", "Contact Us", "Feedback"])

if page == "Home":

    with content_container:
        st.subheader("Welcome to the ABN Lookup Tool!")
        # Adding an image or icon can make it visually appealing
        #st.image("welcome_image.png", width=300)  # Replace with an actual path to an image
        st.write("Follow these steps to get started:")
        st.markdown("""
        1. **Enter Industry**: Specify the industry you are interested in.
        2. **Enter Postcode**: Provide the postcode for the location you want to target.
        3. **Set Page Limit**: Decide the number of pages you want to scrape for business names.
        """)

    st.markdown(
    """
    ***After filling in these details:***
    
    - Click on **'Generate Suggestions'** to get initial business name suggestions related to the entered industry.
    - Proceed with **'Web Scrape and Refine'** to refine the business names after scraping additional data.
    
    ***You can also edit the generated and refined suggestions. Once you are satisfied with the suggestions:***
    
    - Click **'Explore Businesses Now'** to retrieve and display information about businesses related to the selected industry and postcode.
    
    Feel free to navigate through the tool and explore the various features available!

    Current running Status:
    """
    )

    sidebar.header("User Input Features")
    st.session_state.industry_input = sidebar.text_input("Enter Industry:", value=st.session_state.industry_input)
    st.session_state.postcode_input = sidebar.text_input("Enter Postcode:", value=st.session_state.postcode_input, max_chars=4)
    st.session_state.page_number = sidebar.number_input("Enter Page Limit to Scrape:", value=st.session_state.page_number, min_value=1, max_value=25, step=1)

    if sidebar.button("Generate Suggestions"):
        with st.spinner('Generating Initial Business Name Suggestions...'):
            initial_suggestions = generate_business_name_suggestions(st.session_state.industry_input)
            while not initial_suggestions:
                st.warning("No initial suggestions generated. Regenerating...")
                initial_suggestions = generate_business_name_suggestions(st.session_state.industry_input)
            st.session_state.initial_suggestions = initial_suggestions
            st.success(f"Generated initial suggestions for {st.session_state.industry_input}")

    # Button to Perform Web Scraping and Refine Suggestions
    if sidebar.button("Web Scrape and Refine"):
        st.session_state.explore_businesses = False
        if st.session_state.industry_input:
            with st.spinner('Scraping and Refining Business Names...'):
                scraped_names = get_all_business_names(st.session_state.industry_input, st.session_state.page_number)
                st.session_state.scraped_names = scraped_names
                st.success(f"Scraped {len(scraped_names)} business names for {st.session_state.industry_input}")
                refined_names = refine_business_names(st.session_state.industry_input, scraped_names)
                st.session_state.refined_names = refined_names
                # Check if initial_suggestions is None before concatenation
                if st.session_state.initial_suggestions is None:
                    st.session_state.initial_suggestions = []  # Initialize it as an empty list if it's None
                st.session_state.combined_suggestions = list(set(st.session_state.initial_suggestions + refined_names))
                st.success(f"Refined and combined suggestions for {st.session_state.industry_input}")
        else:
            st.warning("Please provide the industry before scraping and refining")

    if st.session_state.initial_suggestions:
        st.subheader(f"Initial suggested Names for {st.session_state.industry_input} Industry:")
        st.session_state.allow_edit_initial = st.radio(
            "Edit Initial Suggested Names?",
            ['Yes', 'No'],
            key="edit_initial",
            index=0 if st.session_state.allow_edit_initial == 'Yes' else 1
        )
        if st.session_state.allow_edit_initial == 'Yes':
            edited_initial_suggestions = st.text_area("Edit Initial Suggested Names:", ', '.join(st.session_state.initial_suggestions))
            st.session_state.initial_suggestions = edited_initial_suggestions.split(', ')
            st.session_state.combined_suggestions = combine_and_deduplicate(st.session_state.initial_suggestions, st.session_state.refined_names)
        else:
            st.write(f"Initial Suggestions: {', '.join(st.session_state.initial_suggestions)}")

    if st.session_state.refined_names:
        st.subheader(f"Refined Names for {st.session_state.industry_input} Industry:")
        st.session_state.allow_edit_refined = st.radio(
            "Edit Refined Names?",
            ['Yes', 'No'],
            key="edit_refined",
            index=0 if st.session_state.allow_edit_refined == 'Yes' else 1
        )
        if st.session_state.allow_edit_refined == 'Yes':
            edited_refined_names = st.text_area("Edit Refined Names:", ', '.join(st.session_state.refined_names))
            # Update the refined_names state
            st.session_state.refined_names = edited_refined_names.split(', ')
            # Update combined_suggestions based on edited refined_names
            st.session_state.combined_suggestions = combine_and_deduplicate(st.session_state.initial_suggestions, st.session_state.refined_names)
        else:
            st.write(f"Refined Names: {', '.join(st.session_state.refined_names)}")

    if st.session_state.combined_suggestions:
        st.subheader(f"Combined Suggestions for {st.session_state.industry_input} Industry:")
        st.session_state.allow_edit_combined = st.radio(
            "Edit Combined Suggestions?",
            ['Yes', 'No'],
            key="edit_combined",
            index=0 if st.session_state.allow_edit_combined == 'Yes' else 1
        )
        if st.session_state.allow_edit_combined == 'Yes':
            edited_combined_suggestions = st.text_area("Edit Combined Suggestions:", ', '.join(st.session_state.combined_suggestions))
            new_combined_suggestions = edited_combined_suggestions.split(', ')

            # Initialize new lists for initial and refined suggestions
            new_initial_suggestions = []
            new_refined_names = []
            
            # Iterate through the new_combined_suggestions and update initial_suggestions and refined_names accordingly
            for suggestion in new_combined_suggestions:
                if suggestion in st.session_state.initial_suggestions:
                    new_initial_suggestions.append(suggestion)
                elif suggestion in st.session_state.refined_names:
                    new_refined_names.append(suggestion)
                else:
                    # Handling the case where the edited suggestion wasn't in either initial or refined names
                    # We are adding the new suggestions to initial suggestions
                    new_initial_suggestions.append(suggestion)

            # Update the state variables
            st.session_state.combined_suggestions = new_combined_suggestions
            st.session_state.initial_suggestions = new_initial_suggestions
            st.session_state.refined_names = new_refined_names
        else:
            st.write(f"Combined Suggestions: {', '.join(st.session_state.combined_suggestions)}")

    if st.button("Explore Businesses Now"):
        if st.session_state.postcode_input:  # Check if a postcode is entered
            if st.session_state.combined_suggestions is not None and st.session_state.combined_suggestions:  # Check if combined_suggestions is not None and not empty
                st.session_state.result_df = None
                with st.spinner('Fetching Business Information...'):
                    postcodes_to_query = {st.session_state.postcode_input}
                    st.session_state.result_df = query_postcodes(postcodes_to_query, st.session_state.combined_suggestions)
                st.session_state.explore_businesses = True
            else:
                st.warning("Please generate and refine suggestions first before exploring businesses.")
        else:
            st.warning("Please enter a postcode before exploring businesses.")

    display_df = None  # Set default value of display_df to None

    if st.session_state.explore_businesses and st.session_state.postcode_input:
        if st.session_state.result_df is not None and not st.session_state.result_df.empty:
            st.subheader(f"Businesses in {st.session_state.postcode_input} related to {st.session_state.industry_input}:")

            # Search bar for ABN or Business Name
            search_term = st.text_input("Search ABN or Business Name:")
            display_df = st.session_state.result_df  # Initialize display_df with result_df
            
            if search_term:
                # Filter the DataFrame based on the search term
                mask = (st.session_state.result_df['ABN'].astype(str).str.contains(search_term)) | \
                    (st.session_state.result_df['Organisation Name'].str.contains(search_term, case=False))
                display_df = st.session_state.result_df[mask]
                
                if display_df.empty:  # check if the filtered DataFrame is empty
                    st.warning("No result to display for the search term. Showing all results instead.")
                    display_df = st.session_state.result_df  # revert to showing all results if the filtered result is empty
            else:
                st.warning("Showing all results. Please enter a search term for specific results.")
            
            # Reset the index of display_df
            display_df = display_df.reset_index(drop=True)

            # Display the (filtered) DataFrame
            st.write('Result DataFrame:', display_df)
        else:
            if not st.session_state.initial_suggestions or not st.session_state.scraped_names or not st.session_state.refined_names or not st.session_state.postcode_input:
                st.warning("Please generate keywords, web scrape, refine, and enter a postcode before exploring businesses.")
    else:
        if not st.session_state.initial_suggestions or not st.session_state.scraped_names or not st.session_state.refined_names or not st.session_state.postcode_input:
            st.warning("Please generate keywords, web scrape, refine, and enter a postcode before exploring businesses.")

    # Before proceeding with CSV and Excel exporting, check if display_df is not None and not empty
    if display_df is not None and not display_df.empty:
        # Now you can safely proceed with your CSV and Excel exporting code

        # CSV exporting code
        csv = display_df.to_csv(index=False)
        csv_bytes = csv.encode('utf-8')
        csv_buffer = io.BytesIO(csv_bytes)

        if 'csv_download_clicked' not in st.session_state:
            st.session_state.csv_download_clicked = False

        if st.download_button('Download CSV', data=csv_buffer, file_name='result_data.csv', mime='text/csv'):
            st.session_state.csv_download_clicked = True

        if st.session_state.csv_download_clicked:
            st.success('CSV Download started!')
            st.session_state.csv_download_clicked = False  # Reset the state after showing the message

        # Excel exporting code
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
    else:
        st.warning("There is no data to export. Please ensure data is loaded and displayed before attempting to export.")

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

# Styling
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