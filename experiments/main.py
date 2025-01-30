# from ollama import chat
# from ollama import ChatResponse

# stream = chat(
#     model='deepseek-r1:1.5b',
#     messages=[{'role': 'user', 'content': 'Why is the sky blue? Think about it.'}],
#     stream=True,
# )

# for chunk in stream:
#     print(chunk['message']['content'], end='', flush=True)

# from ollama import Client
# client = Client(
#   host='http://localhost:11434',
#   headers={'x-some-header': 'some-value'}
# )
# response = client.chat(model='deepseek-r1:1.5b', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])

import asyncio
from ollama import AsyncClient

async def chat():
  message = {'role': 'user', 'content': 'Why is the sky blue?'}
  async for part in await AsyncClient().chat(model='deepseek-r1:32b', messages=[message], stream=True):
    print(part['message']['content'], end='', flush=True)

asyncio.run(chat())