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
#Set Up openai API key
openai.api_key = os.getenv("OPENAI_API_KEY")

#Define langchain prompttemplate
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

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        print(request.POST) 
        user_message = request.POST.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status = 400)
        
        try:
            #generate a response using langchain
            bot_response = "I'm currently unavailable due to high demand. Please try again later."
              # bot_response = chain.run(message=user_message)
            return JsonResponse({'message': bot_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status = 500)
            
    return render(request, 'chatbot.html')