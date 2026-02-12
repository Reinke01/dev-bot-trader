from agno.models.google import Gemini
# from agno.models.groq import Groq
from agno.models.message import Message

from dotenv import load_dotenv
load_dotenv()

model = Gemini(id="gemini-2.5-flash")

msg = Message(
    role="user",
    content="Olá, sou dev e faço parte do GDG Foz"
)

response = model.invoke([msg])

print(response.candidates[0].content.parts[0].text)


# Groq
# model = Groq(id="llama-3.3-70b-versatile")

# msg = Message(
#     role="user",
#     content=[{
#         "type": "text",
#         "text": "Olá, sou dev e faço parte do GDG Foz"
#     }]
# )

# response = model.invoke([msg])

# print(response.choices[0].message.content)