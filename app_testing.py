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