import os
import openai
 
openai.api_key = os.environ["OPENAI_API_KEY"]

# Define a function to generate business name suggestions
def generate_business_name_suggestions(industry):
    # Define a prompt that includes the industry
    prompt = f"Generate unique one-word keywords strictly related to {industry} businesses:"

    # Use the OpenAI API to generate suggestions
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use GPT-3.5 Turbo for chat-based models
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates unique one-word keywords strictly related to business names, which can be "
             "used to search for all the businesses in any yellow pages directory. Also those should be singular and not plural if possible"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,  # Adjust the max_tokens based on your needs
        n=25,  # Number of suggestions to generate
        stop=None,  # Specify stop words to end the generation
        temperature=0.7  # Adjust the temperature for randomness
    )

    # Extract the suggestions from the API response
    suggestions = response['choices'][0]['message']['content']

    # Remove the numbers and split the suggestions into a list
    suggestions = [name.strip() for name in suggestions.split('\n') if name.strip()]

    return suggestions