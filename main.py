from fasthtml.common import *
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

MAX_NAME_LENGTH = 15
MAX_MESSAGE_LENGTH = 50


import json

def serialize_message(message):
    if isinstance(message, HumanMessage):
        return {
            "type": "HumanMessage",
            "content": message.content
        }
    elif isinstance(message, AIMessage):
        return {
            "type": "AIMessage",
            "content": message.content
        }
    elif isinstance(message, SystemMessage):
        return {
            "type": "SystemMessage",
            "content": message.content
        }
    else:
        raise TypeError(f"Object of type {type(message).__name__} is not JSON serializable")

def add_message(message):
    serialized_message = serialize_message(message)
    supabase.table("messages").insert({
        "message": json.dumps(serialized_message),
    }).execute()

def deserialize_message(serialized_message):
    message_dict = json.loads(serialized_message)
    message_type = message_dict["type"]
    content = message_dict["content"]
    
    if message_type == "HumanMessage":
        return HumanMessage(content=content)
    elif message_type == "AIMessage":
        return AIMessage(content=content)
    elif message_type == "SystemMessage":
        return SystemMessage(content=content)
    else:
        raise TypeError(f"Unknown message type: {message_type}")

def get_messages():
    response = (
        supabase.table("messages").select("*").order("created_at").execute()
    )
    messages = [deserialize_message(record["message"]) for record in response.data]
    return messages          

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


def ChatMessage(msg_idx, **kwargs):
    messages = get_messages()
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
        placeholder="Type your message here....",
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
    messages = get_messages()
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
        add_message(
            HumanMessage(content=user_input)
        )
        
        messages = get_messages()
            
        response = model.invoke(
            [
                SystemMessage(
                    content="Respond like a prirate"
                ),
                HumanMessage(content=user_input)
            ]
        )
        
        add_message(
            AIMessage(content=response.content)
        )
        
        messages = get_messages()
        return Div(
            *[
                ChatMessage(i) for i in range(len(messages))
            ]
        )
            
    
serve()
