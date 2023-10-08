import os
import openai
import re
from webscrapping import get_all_business_names

openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_business_name_suggestions(industry, page_number):
    # Define a prompt to generate initial suggestions
    initial_prompt = f"Please generate a list of unique, one-word keywords that are strictly and directly related to the {industry} industry. These keywords should be commonly associated with businesses in the {industry} sector and should not include generic words or phrases."

    # Query GPT with the initial prompt
    initial_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": initial_prompt}],
        max_tokens=100,
        temperature=0.7
    )

    # Extract and parse the initial suggestions from GPT's response
    initial_suggestions_text = initial_response['choices'][0]['message']['content']
    initial_suggestions = re.findall(r'\b[A-Z][a-z]*\b', initial_suggestions_text)
    initial_suggestions = [word.capitalize() for word in initial_suggestions if word.isalpha()]
    print(initial_suggestions)
    # Refine business names
    #additional_names = get_all_business_names(industry)
    additional_names = get_all_business_names(industry, page_number)

    refine_prompt = f"The following is a list of business names related to the {industry} industry: {', '.join(additional_names)}. You can keep the parts of business names that might sound related but might not exactly correspond to typical keywords in the {industry} industry. For example, for 'Sydney Side Pest' and 'Bugz Off' in the Pest Control Industry, keep 'Pest' and 'Bugz' but remove 'Sydney', 'Side' and 'Off'. Please carefully review the list. For each word, if it isn't a word a strictly related to the {industry} industry, kindly remove it, even if it forms a part of a business name. Leaving behind a list of words that are uniquely and very strictly related to the {industry} industry."
    refine_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": refine_prompt}],
        max_tokens=500,
        temperature=0.7
    )
    refined_names_text = refine_response['choices'][0]['message']['content']
    refined_names = re.findall(r'\b[A-Z][a-z]*\b', refined_names_text)
    refined_names = [word.capitalize() for word in refined_names if word.isalpha()]
    #Testing
    print(refined_names)
    # Combine and deduplicate
    combined_suggestions = list(set(initial_suggestions + refined_names))

    return initial_suggestions, refined_names, combined_suggestions

def combine_and_deduplicate(initial, refined):
    """Combine and deduplicate suggestions."""
    return list(set(initial + refined))
