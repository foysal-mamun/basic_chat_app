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
app = FastHTML(hdrs=(tlink, dlink, picolink), ws_hdr=True)

model = ChatOpenAI(
    model_kwargs={
        "stream": True
    }
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
        name="msg",
        id="msg-input",
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
        ws_send="",
        hx_ext="ws",
        ws_connect="/wscon",
        cls="flex space-x-2 mt-2"
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
    
# def render_chat_page():
#     return Body(
#         H1("Chatbot Demo"),
#         Div(
#             *[ChatMessage(idx) for idx in range(len(messages))],
#             id="chatlist",
#             cls="chat-box overflow-y-auto",
#         ),
#         ,
#         cls="p-4 max-w-lg mx-auto",
#     )
    
@app.route("/")
def get():
    page = render_home_page()
    return Title("Chatbot Demo"), page

@app.ws("/wscon")
async def wscon(msg: str, send):
    messages.append(HumanMessage(content=msg))
    print("messages", messages)
    
    await send(
        Div(
            ChatMessage(
                len(messages) - 1,
            ),
            hx_swap_oob="beforeend",
            id="chatlist"
        )
    )
    await send(
        ChatInput()
    )
    
    messages.append(AIMessage(content=""))
    await send(
        Div(ChatMessage(len(messages) - 1), hx_swap_oob="beforeend", id="chatlist")
    )
    for chunk in model.stream(input=[sp] + messages):
        chunkval = chunk.content
        print("CHUNKVAL:", chunkval)
        messages[-1].content += chunkval
        await send(
            Span(
                chunkval,
                id=f"chat-content-{len(messages)-1}",
                hx_swap_oob="beforeend",
            )
        )
        await asyncio.sleep(0.05)
        
    
serve()