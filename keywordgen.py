'''
import os
import openai
import re
 
openai.api_key = os.environ["OPENAI_API_KEY"]

# Define a function to generate business name suggestions
def generate_business_name_suggestions(industry):
    # Define a prompt that includes the industry
    prompt = f"Please generate a list of unique, one-word keywords that are strictly and directly related to the {industry} industry. These keywords should be commonly associated with businesses in the {industry} sector and should not include generic words or phrases."

    # Use the OpenAI API to generate suggestions
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 Turbo for chat-based models
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,  # Adjust the max_tokens based on your needs
        temperature=0.7  # Adjust the temperature for randomness
    )

    # Extract the suggestions from the API response
    suggestions_text = response['choices'][0]['message']['content']

    # Parse and format the suggestions using regular expressions
    suggestions = re.findall(r'\b[A-Z][a-z]*\b', suggestions_text)
    suggestions = [word.capitalize() for word in suggestions if word.isalpha()]

    return suggestions
'''

import os
import openai
import re

openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_business_name_suggestions(industry, additional_names):
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
    additional_names = ["Bugz Off", "Sydney Side Pest", "Pest Control", "Pesticides"]
    refine_prompt = f"The following is a list of business names related to the {industry} industry: {', '.join(additional_names)}. You can keep the parts of business names that might sound related but might not exactly correspond to typical keywords in the {industry} industry. For example, for 'Sydney Side Pest' and 'Bugz Off' in the Pest Control Industry, keep 'Pest' and 'Bugz' but remove 'Sydney', 'Side' and 'Off'. Please carefully review the list. For each word, if it isn't a word a little related to the {industry} industry, kindly remove it, even if it forms a part of a business name. Leaving behind a list of words that are uniquely related to the {industry} industry."
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
    # Step 3: Combine and deduplicate
    combined_suggestions = list(set(initial_suggestions + refined_names))

    return initial_suggestions, refined_names, combined_suggestions
'''
    # Testing
    print(initial_suggestions)
    # Combine the initial suggestions with the additional names
    combined_suggestions = list(set(initial_suggestions + additional_names))
    print(combined_suggestions)
    # Define a second prompt to verify the relevance of the combined suggestions
    verification_prompt = f"""
    The following is a list of words, each word being either a keyword or a business name related to the {industry} industry: {', '.join(combined_suggestions)}. 
    The keywords are strictly related to the {industry} industry. However, you can keep the parts of business names which might sound related but might not 
    exactly correspond to typical keywords in the {industry} industry. For example, for 'Sydney Side Pest' and 'Bugz Off' in Pest Control Industry, keep 'Pest' and 'Bugz' but remove 'Sydney', 'Side' and 'Off'. 
    Please carefully review the list. For each word, if it isn't a word strictly related to the {industry} industry, kindly remove it, even if it forms part of a business name. 
    Additionally, please eliminate any duplicates, leaving behind a list of words that are uniquely and directly related to the {industry} industry.
    """

    # Query GPT with the verification prompt
    verification_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": verification_prompt}],
        max_tokens=500,
        temperature=0.7
    )

    # Extract, parse, and return the final suggestions from GPT's response
    final_suggestions_text = verification_response['choices'][0]['message']['content']
    final_suggestions = re.findall(r'\b[A-Z][a-z]*\b', final_suggestions_text)
    final_suggestions = [word.capitalize() for word in final_suggestions if word.isalpha()]

    return final_suggestions
'''
