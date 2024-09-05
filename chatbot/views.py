from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
from langchain_openai import OpenAI
# from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Create your views here.

#using openai to get bot responses
# Set Up openai API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define langchain prompttemplate
template = """ 
You are an AI mental health therapist. You help students
with their mental health issues.
The student says : "{message}"
Respond in a kind and helpful manner
"""
prompt = PromptTemplate(input_variables=["message"], template=template)

#Initialize the langchain with openai model
llm = OpenAI(temperature = 0.7)
chain = LLMChain(llm = llm, prompt = prompt)


#using a csv file to get bot responses
# import pandas as pd
# import re
# # from fuzzywuzzy import process

# data_path = os.path.join(os.path.dirname(__file__), 'data', 'Mental_Health_FAQ.csv')
# df = pd.read_csv(data_path, encoding='ISO-8859-1')
# print(f"DataFrame Loaded: {df.head()}") 

# def get_response(user_message):
# #     # questions = df['Questions'].tolist()
# #     # # Use fuzzy matching to find the best match
# #     # best_match = process.extractOne(user_message, questions)
    
# #     # if best_match[1] > 80:  # Only consider matches with a score higher than 80%
# #     #     matched_row = df[df['Questions'] == best_match[0]].iloc[0]
# #     #     return matched_row['Answers']
# #     # return "I'm sorry, I don't have an answer for that. Please reach out to a professional counselor for help."
#     if df is None:
#         print("DataFrame is not loaded properly.")
#         return "Sorry, I am having trouble accessing the data right now."

#     # Check if 'Questions' column exists
#     if 'Questions' not in df.columns:
#         print("Column 'Questions' does not exist in DataFrame.")
#         return "Sorry, I am having trouble accessing the data right now."

#     # Normalize the user message
#     user_message = user_message.lower()

#     # Iterate through the DataFrame
#     for index, row in df.iterrows():
#         # Compile the pattern with case-insensitive flag
#         pattern = re.compile(re.escape(row['Questions'].lower()), re.IGNORECASE)
#         if pattern.search(user_message):
#             print(f"Match found: {row['Questions']} -> {row['Answers']}")
#             return row['Answers']

#     return "I'm sorry, I don't have an answer for that. Please reach out to a professional counselor for help."



#using json file to get bot responses
import json
json_path = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'intents.json')
with open(json_path, 'r') as file:
    intents = json.load(file)

#Check similarities using re
# import re
# def get_response(user_message):
#     user_message = user_message.lower()
#     for intent in intents['intents']:
#         for pattern in intent['patterns']:
#             # Use regex to check if the pattern is in the user message
#             if re.search(re.escape(pattern.lower()), user_message):
#                 return intent['responses'][0]
#     return None

#check similarities in trained question and response using spacy
import spacy
nlp = spacy.load("en_core_web_md") 

def get_response(user_message):
    user_doc = nlp(user_message.lower())
    max_similarity = 0
    best_match = None
    
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            pattern_doc = nlp(pattern.lower())
            similarity = user_doc.similarity(pattern_doc)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = intent['responses'][0]
    
    if max_similarity > 0.5:  # Threshold for similarity
        return best_match
    return None

#without checking for similarities
# def get_response(user_message):
#     for intent in intents['intents']:
#         for pattern in intent['patterns']:
#             if pattern.lower() in user_message.lower():
#                 return intent['responses'][0]
#     response = openai.Completion.create(
    #     engine="text-davinci-003",
    #     prompt=f"User said: {user_message}\nRespond appropriately:",
    #     max_tokens=50
    # )
    # return response.choices[0].text.strip()

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        print(request.POST) 
        user_message = request.POST.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status = 400)
        
        try:
            bot_response = get_response(user_message)
            
            # If no response is found, use OpenAI
            if bot_response is None:
                bot_response = chain.run(message=user_message)
                
            return JsonResponse({'message': bot_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status = 500)
            
    return render(request, 'chatbot.html')