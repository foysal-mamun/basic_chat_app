from fasthtml.common import *

app, rt = fast_app(
    hdrs=(
        Link(
            rel="icon",
            type="assets/x-icon",
            href="/assets/favicon.png"
        ),
    )
)
    
def render_content():
    return Div(
        H1("FastHTML Chat App 💬"),
    )

@rt("/")
def get():
    return Titled(
        "FastHTML Chat App 💬",
        render_content()
    )
    
serve()