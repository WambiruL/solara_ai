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
import re
import random
def get_response(user_message):
    user_message = user_message.lower()
    
    for intent in combined_intents:  # Iterate through the list directly
        for pattern in intent['patterns']:
            if re.search(re.escape(pattern.lower()), user_message):
                return random.choice(intent['responses'])  # Randomly select a response
              
    return "I'm sorry, I didn't understand that. Can you try rephrasing?"

#no checking for similarities
# import random
# def get_response(user_message):
#     user_message = user_message.lower()
    
#     for intent in combined_intents:
#         for pattern in intent['patterns']:
#             if pattern.lower() in user_message:
#                 return random.choice(intent['responses'])
    
#     return "I'm sorry, I didn't understand that. Can you try rephrasing?"


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
