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
    refine_prompt = f"Carefully examine the following list of words and phrases related to the {industry} industry: {', '.join(additional_names)}. Your task is to rigorously filter the list, ensuring that only words or phrases with a direct, exclusive, and unambiguous connection to the {industry} industry are retained. Exclude words or phrases that, while they may appear in business names within the industry, do not have a clear and unique association with the industry itself. For example, general terms like 'Solutions', 'Services', 'Systems' or geographical names should be removed. Compile a new list that includes only words or phrases with a clear, unique, and strict relevance to the {industry} industry, and ensure to omit all function words like 'all', 'the', 'mr', 'dr', 'pty', 'ltd', etc."

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
