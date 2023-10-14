import openai
import re
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not set")

def generate_business_name_suggestions(industry):
    initial_prompt = f"Please generate a diverse and specific list of unique, single-word keywords that are strictly and directly related to the {industry} industry, ensuring no repetition of words. The keywords should be widely recognized and associated with businesses in the {industry} sector, excluding any generic or broadly applicable words or phrases. Emphasize words that have a clear and unique association with the {industry} industry."

    initial_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": initial_prompt}],
        max_tokens=500,
        temperature=0.7
    )

    initial_suggestions_text = initial_response['choices'][0]['message']['content']
    initial_suggestions = re.findall(r'\b[A-Z][a-z]*\b', initial_suggestions_text)
    initial_suggestions = [word.capitalize() for word in initial_suggestions if word.isalpha()]
    return initial_suggestions

def refine_business_names(industry, additional_names):
    refine_prompt = f"Please scrutinize the following list of words and phrases associated with the {industry} industry: {', '.join(additional_names)}. Ensure that only words or phrases with a direct, exclusive, and unambiguous connection to the {industry} industry are retained. Exclude words or phrases that might be present in business names but do not have a clear and unique association with the industry itself. For instance, general terms like 'Solutions', 'Services', 'Systems', and geographical names should be omitted. Retain words or phrases that are terminologies, tools, or commonly associated with the {industry} industry, and omit all function words like 'all', 'the', 'mr', 'dr', 'pty', 'ltd', etc. For example, in the pest control industry, words like 'termite', 'exterminate', or 'infestation' should be retained, while 'Advanced', 'Solutions', or 'Wollongong' should be excluded."

    refine_response = openai.ChatCompletion.create(
        model="gpt-4-0314",
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
