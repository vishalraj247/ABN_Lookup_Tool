import openai
import re
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_business_name_suggestions(industry):
    initial_prompt = f"Please generate a list of unique, one-word keywords that are strictly and directly related to the {industry} industry. These keywords should be commonly associated with businesses in the {industry} sector and should not include generic words or phrases."

    initial_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": initial_prompt}],
        max_tokens=100,
        temperature=0.7
    )

    initial_suggestions_text = initial_response['choices'][0]['message']['content']
    initial_suggestions = re.findall(r'\b[A-Z][a-z]*\b', initial_suggestions_text)
    initial_suggestions = [word.capitalize() for word in initial_suggestions if word.isalpha()]
    return initial_suggestions

def refine_business_names(industry, additional_names):
    refine_prompt = f"The following is a list of business names related to the {industry} industry: {', '.join(additional_names)}. Please carefully review the list. For each word, if it isn't a word strictly related to the {industry} industry, kindly remove it, even if it forms a part of a business name. Leave behind a list of words that are uniquely and very strictly related to the {industry} industry."

    refine_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": refine_prompt}],
        max_tokens=500,
        temperature=0.7
    )
    
    refined_names_text = refine_response['choices'][0]['message']['content']
    refined_names = re.findall(r'\b[A-Z][a-z]*\b', refined_names_text)
    refined_names = [word.capitalize() for word in refined_names if word.isalpha()]
    return refined_names

def combine_and_deduplicate(initial, refined):
    """Combine and deduplicate suggestions."""
    if initial is None:
        initial = []
    if refined is None:
        refined = []
    return list(set(initial + refined))
