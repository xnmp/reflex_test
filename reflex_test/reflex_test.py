"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config


from .frontend.layout import lhs_sidebar, rhs
from .frontend.style import style



def index() -> rx.Component:
    return rx.hstack(lhs_sidebar(), rhs())


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="teal",
    ),
    style=style,
    stylesheets=[
        'https://unpkg.com/react-tagsinput/react-tagsinput.css',
        "https://unpkg.com/react-date-range/dist/styles.css",
        "https://unpkg.com/react-date-range/dist/theme/default.css",
        # "https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-grid.css",
        # "https://cdn.jsdelivr.net/npm/@glideapps/glide-data-grid@6.0.3/dist/index.min.css",
        # "https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-theme-alpine.css",
    ],
    tailwind={
        "theme": {
            "extend": {},
        },
        "plugins": ["@tailwindcss/typography"],
    },
)

app.add_page(index)

