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
