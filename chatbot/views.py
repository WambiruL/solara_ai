from django.conf import settings
from .models import Chat, Feedback
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
# load_dotenv()


# Create your views here.

#using json file to get bot responses
import json
json_path_intents = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'intents.json')
with open(json_path_intents, 'r') as file:
    intents_data = json.load(file)

json_path_kb = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'KB.json')
with open(json_path_kb, 'r') as file:
    kb_data = json.load(file)
    
combined_intents = intents_data['intents'] + kb_data['intents']
    
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
import random
import concurrent.futures
nlp = spacy.load("en_core_web_md") 
cached_patterns = [
    (nlp(pattern.lower()), intent.get('responses', ["I'm sorry, I didn't understand that. Can you try rephrasing?"]))
                   for intent in combined_intents
                   for pattern in intent.get('patterns', [])
]

def compare_pattern(user_doc, pattern_doc, responses):
    if user_doc.vector_norm and pattern_doc.vector_norm:
        return user_doc.similarity(pattern_doc), random.choice(responses)
    return 0, None
         
def get_response(user_message):
    user_doc = nlp(user_message.lower())
    max_similarity = 0
    best_match = None
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        #submit pattern comparison tasks to the executor
        futures = [
            executor.submit(compare_pattern, user_doc, pattern_doc, responses)
            for pattern_doc, responses in cached_patterns
        ]
        for future in concurrent.futures.as_completed(futures):
            similarity, response = future.result()
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = response
    
    if max_similarity > 0.5:  # Threshold for similarity
        return best_match
    return "I'm sorry, I didn't understand that. Can you try rephrasing?"

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
    
    #retrieve chat history
    if request.method == 'GET' and request.user.is_authenticated:
        chats = Chat.objects.filter(user = request.user).order_by('timestamp')
        chat_history = [{'message': chat.message, 'is_user':chat.is_user} for chat in chats]
        
        return render(request, 'chatbot.html', {'chat_history':chat_history})
    
    #main code to display user's and bot's chats
    if request.method == 'POST':
        # print(request.POST) 
        user_message = request.POST.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status = 400)
        
        #save user's message to the chat model
        if request.user.is_authenticated:
            Chat.objects.create(user = request.user, message = user_message, is_user = True)
        
        try:
            bot_response = get_response(user_message)
            # # If no response is found, use OpenAI
            # if bot_response is None:
            #     bot_response = chain.run(message=user_message)
                
            #save bot's response to the chat model
            if request.user.is_authenticated:
                Chat.objects.create(user = request.user, message = bot_response, is_user = False)
                
            return JsonResponse({'message': bot_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status = 500)
          
    return render(request, 'chatbot.html')

@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        feedback = data.get('feedback')
        
        #store in database
        Feedback.objects.create(feedback = feedback)
        
        return JsonResponse({'status': 'success', 'message': 'Feedback received!'})
    return JsonResponse({'status':'error', 'message':'Invalid request'}, status = 400)
