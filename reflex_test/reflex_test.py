"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config


from .layout.left_bar import sidebar
# from .sidebar import sidebar
from .layout.instantiate import filters, constellation, word_freq_bar
from .style import style


def rhs() -> rx.Component:
    return rx.vstack(
        rx.hstack(constellation.element, word_freq_bar.element, spacing="5"),
        rx.vstack(filters.element, max_height="50vh"),
        spacing="5",
        justify="center",
        max_height="95vh",
    )


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
            max_height="85vh",
        ),
        rx.logo(),
    )
    
    return rx.hstack(sidebar(), rhs())


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


