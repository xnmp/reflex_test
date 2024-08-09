"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from .frontend.layout import index
from .frontend.style import style, stylesheets
from .frontend.theme import theme


app = rx.App(
    theme=theme,
    style=style,
    stylesheets=stylesheets,
    tailwind={
        "theme": {
            "extend": {},
        },
        "plugins": ["@tailwindcss/typography"],
    },
)

app.add_page(index)
