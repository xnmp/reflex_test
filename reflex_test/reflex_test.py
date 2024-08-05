"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config


from .layout.left_bar import sidebar
# from .sidebar import sidebar
from .layout.instantiate import filters
from .style import style


def index() -> rx.Component:
    # Welcome Page (Index)
    welcome = rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            # filters.element,
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )
    
    return rx.hstack(sidebar(), filters.element)


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="teal",
    ),
    style=style,
    stylesheets=[
        # "https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-grid.css",
        # "https://cdn.jsdelivr.net/npm/@glideapps/glide-data-grid@6.0.3/dist/index.min.css",
        # "https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-theme-alpine.css",
    ],
)

app.add_page(index)


