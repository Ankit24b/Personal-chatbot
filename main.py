from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key= os.getenv('OPENAI_API_SECRET_KEY'))
"""
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{
        'role': 'system',
        'content': 'You are a CEO of Apple'
    }, {'role': 'assistant',
        'content': 'iPhone is awesome'
    }, {'role': 'user',
        'content': 'What year was this released?'
    }]
)

print(response)


response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{
        'role': 'system',
        'content': 'You are a CEO of Apple'
    }, {'role': 'assistant',
        'content': 'iPhone is awesome'
    }, {'role': 'user',
        'content': 'What year was this released?'
    }],
    temperature=0.6
)

print(response.choices[0].message.content)

"""

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

chat_log = [{'role': 'system', 'content': 'You are a Python tutor AI!'}]

"""
while True:

    user_input = input()

    if user_input.lower() == 'stop':
        break

    chat_log.append({'role': 'user', 'content': user_input})

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=0.6
    )

    bot_response = response.choices[0].message.content
    chat_log.append({'role': 'assistant', 'content': bot_response})

    print(bot_response)
"""

chat_responses = []


@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()
    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=chat_log,
                temperature=0.5,
                stream=True
            )

            ai_response = ''

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break




@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=0.5
    )

    bot_response = response.choices[0].message.content
    chat_log.append({'role': 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})