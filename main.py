from fasthtml.common import *
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

import asyncio

load_dotenv()

tlink = (Script(src="https://unpkg.com/tailwindcss-cdn@3.4.3/tailwindcss.js"),)
dlink = Link(
    rel="stylesheet",
    href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
)

fLink = Link(
    rel="icon",
    type="assets/x-icon",
    href="/assets/favicon.png"
)
app = FastHTML(hdrs=(tlink, dlink, picolink, fLink), ws_hdr=True)

model = ChatOpenAI(
)
sp = SystemMessage(
    content="You are a helpful and concise assistant."
)
messages = []

def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    bubble_class = f"chat-bubble-{'primary' if role == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if role == 'user' else 'start'}"
    
    return Div(
        Div(role, cls="chat-bubble"),
        Div(
            msg.content,
            id=f"chat-content-{msg_idx}",
            cls=f"chat-bubble {bubble_class}"
        ),
        id=f"chat-message-{msg_idx}",
        cls=f"chat {chat_class}",
        **kwargs
    )
    
def ChatInput():
    return Input(
        type="text",
        name="user_input",
        id="user_input",
        placeholder="Type your message here...",
        cls="input input-bordered w-full max-w-xs",
        hx_swap_oob="true"
    )
    
def ChatForm():
    return Form(
        Group(
            ChatInput(),
            Button(
                "Send",
                cls="btn btn-primary"
            )
        ),
        method="post",
        action="/chat",
        hx_post="/chat",
        hx_target="#chatlist",
        hx_swap="innerHTML",
        cls="mt-4"
        
    )
    
def render_home_page():
    return Body(
        H1("FastHTML Chat App 💬"),
        Div(
            *[
                ChatMessage(i) for i in range(len(messages))
            ],
            id="chatlist",
            cls="chat-box overflow-y-auto"
        ),
        ChatForm(),
        cls="p-4 max-w-lg mx-auto"
    )
    
@app.route("/")
def get():
    page = render_home_page()
    return Title("Chatbot Demo"), page

@app.route("/chat")
def chat( user_input: str):
    if user_input:
        messages.append(
            HumanMessage(content=user_input)
        )
        
        response = model.invoke(
            [
                SystemMessage(
                    content="Respond like a prirate"
                ),
                *messages
            ]
        )
        
        print(response)
        
        messages.append(
            AIMessage(content=response.content)
        )
        
        return Div(
            *[
                ChatMessage(i) for i in range(len(messages))
            ]
        )
            
    
serve()