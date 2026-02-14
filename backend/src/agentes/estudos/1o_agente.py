from agno.models.groq import Groq
from agno.models.message import Message

from dotenv import load_dotenv
load_dotenv()

model = Groq(id="llama-3.3-70b-versatile")

msg = Message(
    role="user",
    content=[{
        "type": "text",
        "text": "Qual o preço do Bitcoin nesse momento?"
    }]
)

response = model.invoke([msg])

print(response.choices[0].message.content)