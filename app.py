import streamlit as st
import pandas as pd
import os
import io
from PIL import Image, ImageDraw

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

if 'previous_industry_input' not in st.session_state:
    st.session_state.previous_industry_input = ""

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

def circular_crop(image_path, output_size):
    with Image.open(image_path) as im:
        # Create a mask of the same size as the image, filled with 0 (black)
        mask = Image.new("L", im.size, 0)
        
        # Draw a white circle on the mask
        draw = ImageDraw.Draw(mask)
        width, height = im.size
        draw.ellipse((0, 0, width, height), fill=255)
        
        # Apply the mask to the image
        circular_cropped = Image.composite(im, Image.new("RGBA", im.size, (0, 0, 0, 0)), mask)
        
        # Resize the image to the desired size
        circular_cropped = circular_cropped.resize((output_size, output_size))
        
        return circular_cropped

with header_container:
    col1, col2 = st.columns([1, 15])
    
    with col1:
        cropped_image = circular_crop("App icon.png", 50)  # Adjust the size as needed
        st.image(cropped_image, width=50)  # Adjust the width as needed
    
    with col2:
        st.title("ABN Lookup Tool")

sidebar = st.sidebar
sidebar.title("Navigation")
page = sidebar.radio("Select a Page", ["Home", "Contact Us", "Feedback", "Documentation"])

if page == "Home":

    with content_container:
        st.subheader("Welcome to the ABN Lookup Tool!")
        st.image("Cover image.png", width=575)
        st.write("Follow these steps to get started:")
        st.markdown("""
        1. **Enter Industry**: Specify the industry you are interested in.
        2. **Enter Postcode**: Provide the postcode for the location you want to target.
        3. **Set Page Limit**: Decide the number of pages you want to scrape for business names.
        """)

    sidebar.header("User Input Features")

    # Industry Input
    industry_input = sidebar.text_input("Enter Industry:", value=st.session_state.get('industry_input', ''))
    industry_warning_placeholder = sidebar.empty()

    # If there's a valid industry input, display a success message.
    if st.session_state.industry_input.strip():
        industry_warning_placeholder.success("Industry input provided.")
    else:
        industry_warning_placeholder.empty()  # Clear the placeholder if it's empty

    # Check if industry input has changed
    if st.session_state.previous_industry_input != industry_input:
        reset_session_state()  # Reset the session state
        st.session_state.previous_industry_input = industry_input  # Update the previous industry input

    # Postcode Input
    valid_postcode_ranges = [(2000, 2599), (2619, 2899), (2921, 2999)]
    postcode_input = sidebar.text_input("Enter Postcode:", value=st.session_state.get('postcode_input', ''), max_chars=4)
    postcode_placeholder = sidebar.empty()  # Placeholder for success/warning messages for postcode

    # Check if input is digit and in the valid range
    if postcode_input.isdigit():
        postcode = int(postcode_input)
        is_valid_postcode = any(start <= postcode <= end for start, end in valid_postcode_ranges)
        
        if is_valid_postcode:
            postcode_placeholder.success("Valid postcode.")
            st.session_state.postcode_input = postcode_input
        else:
            postcode_placeholder.warning("Invalid postcode. Please enter a postcode within NSW as of the following ranges: "
                    "2000–2599, 2619–2899, 2921–2999.")
    elif postcode_input:  # Only show the warning if there's an input that's not numeric
        postcode_placeholder.warning("Please enter a numerical value for the postcode.")
            
    st.session_state.page_number = sidebar.number_input("Enter Page Limit to Scrape:", value=st.session_state.page_number, min_value=1, max_value=25, step=1)
    # Update industry input in the session state
    st.session_state.industry_input = industry_input

    if sidebar.button("Generate Suggestions"):
        if not industry_input.strip():
            industry_warning_placeholder.warning("Industry input cannot be left empty.")
        else:
            industry_warning_placeholder.success("Industry input provided.")
            status_placeholder = st.empty()
            status_placeholder.info("Current running Status:")
            with st.spinner('Generating Initial Business Name Suggestions...'):
                initial_suggestions = generate_business_name_suggestions(st.session_state.industry_input)
                while not initial_suggestions:
                    st.warning("No initial suggestions generated. Regenerating...")
                    initial_suggestions = generate_business_name_suggestions(st.session_state.industry_input)
                st.session_state.initial_suggestions = initial_suggestions
                st.success(f"Generated initial suggestions for {st.session_state.industry_input}")
                status_placeholder.empty()

    # Button to Perform Web Scraping and Refine Suggestions
    if sidebar.button("Web Scrape and Refine"):
        if not industry_input.strip():
            industry_warning_placeholder.warning("Industry input cannot be left empty.")
        else:
            industry_warning_placeholder.success("Industry input provided.")
            st.session_state.explore_businesses = False
            status_placeholder = st.empty()
            status_placeholder.info("Current running Status:")
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
                status_placeholder.empty()

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
            suggestions_to_use = st.session_state.combined_suggestions
            # Fallback to initial suggestions if no combined suggestions are available
            if not suggestions_to_use:
                suggestions_to_use = st.session_state.initial_suggestions
            if suggestions_to_use:  # Check if there are suggestions to use (initial or combined)
                st.session_state.result_df = None
                status_placeholder = st.empty()
                status_placeholder.info("Current running Status:")
                with st.spinner('Fetching Business Information...'):
                    postcodes_to_query = {st.session_state.postcode_input}
                    st.session_state.result_df = query_postcodes(postcodes_to_query, suggestions_to_use)
                st.session_state.explore_businesses = True
                status_placeholder.empty()
            else:
                st.warning("Please generate suggestions first before exploring businesses.")
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
            st.session_state['display_df'] = display_df
            # Display the (filtered) DataFrame
            st.write('Result DataFrame:', display_df)
        else:
            if not st.session_state.initial_suggestions or not st.session_state.scraped_names or not st.session_state.refined_names or not st.session_state.postcode_input:
                st.warning("Please atleast generate keywords, or web scrape & refine, and enter a postcode before exploring businesses.")
    else:
        if not st.session_state.initial_suggestions or not st.session_state.scraped_names or not st.session_state.refined_names or not st.session_state.postcode_input:
            st.warning("Please atleast generate keywords, or web scrape & refine, and enter a postcode before exploring businesses.")

    # Before proceeding with CSV and Excel exporting, check if display_df is not None and not empty
    if display_df is not None and not display_df.empty:
        # Now we can safely proceed with our CSV and Excel exporting code

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
    st.write("We value your feedback! Please provide it by clicking [here](https://forms.gle/wuZkSzQ4NK2Pm6pB8).")

elif page == "Documentation":
    # Create Tabs
    chapter1, chapter2, chapter3 = st.tabs(["Chapter 1: Introduction", "Chapter 2: Interface Guide", "Chapter 3: Future & Limitations"])
    
    # Chapter 1 Content
    with chapter1:
        st.markdown(
            """
            ## Introduction
            
            ### Purpose
            The ABN Lookup Tool has been developed with the primary objective of simplifying the process of searching, retrieving, and managing business details. It offers a user-friendly interface coupled with robust features to assist users in gathering comprehensive business-related information.
            
            ### Framework Architecture
            The architecture of the ABN Lookup Tool is modular and designed to provide efficient data retrieval and user interactivity.
            """,
            unsafe_allow_html=True,
        )
        st.image("ABN Lookup Tool Architecture.png", caption="Framework Architecture")
        st.markdown(
            """
            ### Example data
            ```
            | ABN         | Identifier Status | Organisation Name      | Score | Is Current Indicator | State Code | Postcode |
            |-------------|-------------------|------------------------|-------|----------------------|------------|----------|
            | 46103449985 | Active            | PERMANENT PEST CONTROL | 94    | Y                    | NSW        | 2000     |
            | 25618786968 | Active            | Proven Pest Control    | 94    | Y                    | NSW        | 2000     |
            [... More Rows ...]
            ```
            More about the columns:

            - **ABN (Australian Business Number)**: The ABN is a unique 11-digit identifier issued by the Australian government to identify businesses operating in Australia. This column contains the ABNs of various entities, such as businesses and organisations.

            - **Identifier Status**: This column indicates the status of the ABN, which can be "Active" or "Cancelled." An "Active" status means that the business or organisation is currently operating and registered, while a "Cancelled" status suggests that the registration may have been terminated.

            - **Organisation Name**: The organisation name is represented as the legal name or trading name of the entity associated with the ABN. This column contains the full name of the organisation or individual related to the ABN.

            - **Score**: The score here represents a measure of relevance or accuracy of the search results. A higher score indicates a closer match to the search query or keywords. It helps assess the quality of the search results, with higher scores generally being more relevant.

            - **Is Current Indicator**: This column contains a binary indicator ("Y" or "N") that signifies whether the entity's information is current or not. If it's marked as "Y," it means that the data is up-to-date and applicable, while "N" suggests that the information may be outdated or no longer valid.

            - **State Code**: The state code represents the Australian state or territory associated with the entity's physical address. This column provides information about the state or territory in which the entity is located, such as New South Wales (NSW).

            - **Postcode**: The postcode column contains the postal code or ZIP code related to the entity's physical address. It specifies the area or region where the entity is situated, helping to pinpoint its location within a state or territory.

            ### Additional Features
            - **Search and Explore Businesses**: Users can search businesses using either the ABN or Organisation Name. The resulting dataframe (`display_df`) displays the following columns: ABN, Identifier Status, Organisation Name, Score, Is Current Indicator, State Code, and Postcode.

            - **Sort and Fullscreen View**: Users can sort the table by clicking on a column name and view the table in fullscreen for detailed exploration.
            
            - **CSV & Excel Download**: Users can download the search results in CSV or Excel format for future reference.
            
            - **Postcode Specification**: Refine your search by specifying a postcode (NSW Only) to narrow down the results to a particular location.

            - **Session State Management**: The app preserves the state of the home page even when navigating to other pages, ensuring a consistent user experience.

            - **Contact Us**: Users are provided with a direct line of communication (Name, Email, Address) for any inquiries, suggestions, or further communications.

            - **Feedback**: Users can share their thoughts and feedback via our integrated Google Forms, ensuring a straightforward and efficient submission process while keeping all responses systematically organised.

            - **Editing & Updating**: List updates or edits (out of all three) are automatically and dynamically reflected in other relevant lists through a feedback system.
            
            """,
            unsafe_allow_html=True,
        )
    
    # Chapter 2 Content
    with chapter2:
        st.markdown(
            """
            ## Interface Guide
            
            To make the most out of the ABN Lookup Tool, here's a step-by-step guide to navigate through its features, complemented with interface screenshots for clarity.
            
            1. **Startup & Main Page**: Upon launching the tool, you're greeted with the main interface.
            """,
            unsafe_allow_html=True,
        )
        st.image("screenshot_startup.png", caption="Main Page Interface")
        st.markdown(
            """
            2. **Entering Industry Details**: Start by specifying your industry of interest, desired postcode, and setting the page limit.
            """,
            unsafe_allow_html=True,
        )
        st.image("screenshot_industry.png", caption="Industry Input Section", width=300)
        st.markdown(
            """
            3. **Generating Suggestions & Web Scraping**: After filling the initial details, generate business name suggestions and further refine them through web scraping.
            """,
            unsafe_allow_html=True,
        )
        st.image("screenshot_suggestions.png", caption="Generate and Refine Suggestions")
        st.markdown(
            """
            4. **Exploring Businesses**: Post-refinement, explore the businesses based on the refined suggestions and download the data.
            """,
            unsafe_allow_html=True,
        )
        st.image("screenshot_explore.png", caption="Exploring Businesses")
        st.markdown(
            """            
            5. **Feedback & Contact Us Pages**: Navigate to these sections to provide feedback or get in touch with the team.
            """,
            unsafe_allow_html=True,
        )
        st.image("screenshot_contact_feedback.png", caption="Feedback & Contact Sections")
        
    # Chapter 3 Content
    with chapter3:
        st.markdown(
            """
            ## Limitations & Potential Future Improvements
            
            ### Current Limitations:
            - **Geographical Restriction**: The postcode specification currently supports only NSW. Expansion to other regions can make the tool more versatile.
            - **Data Source Dependency**: The data is sourced mainly from YellowPages and ABN Lookup website, which might not cover all available businesses.
            - **Data Accuracy**: As with all web scraping methods, there's always a small chance of discrepancies in the data retrieved.
            - **Keyword Refinement**: Although, final suggestions can be edited, keywords refinement solely depends on GPT-4 API.
            
            ### Future Improvements:
            - **Expanding Geographical Coverage**: Integration of more regions beyond NSW.
            - **Incorporating More Data Sources**: Including more sources can improve the diversity and accuracy of business data.
            - **Improve Refinement Process**: Improve the refinement process of keywords related to the business names of the industry defined.
            - **User Profile Management**: Allow users to create profiles, save searches, and manage their lookup histories.
            - **Feedback Analytics**: Implement an analytics system to derive insights from user feedback and drive future improvements.
            """,
            unsafe_allow_html=True,
        )
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