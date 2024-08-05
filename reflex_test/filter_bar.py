import reflex as rx

from .components.filters import dropdowns, Filters



def accordion() -> rx.Component:
    
    item1 = rx.vstack(
        dropdowns['flavor'].element,
        rx.text(f"Selected: {dropdowns['flavor'].selected_option}"),
    )
    
    item2 = rx.vstack(
        dropdowns['color'].element,
        rx.text(f"Selected: {dropdowns['color'].selected_option}"),
    )
    
    return rx.accordion.root(
        rx.accordion.item(
            header="First Item",
            content=item1,
        ),
        rx.accordion.item(
            header="Second Item",
            content=item2,
        ),
        rx.accordion.item(
            header="Third item",
            content="The third accordion item's content",
        ),
        width="100%",
        type="multiple",
        collapsible=True,
        variant="surface",
    )



def sidebar() -> rx.Component:
    
    logo = rx.image(
        src="/logo.jpg",
        width="2.25em",
        height="auto",
        border_radius="25%",
    )
    
    header = rx.hstack(
        logo,
        rx.heading(
            "Reflex Dashboard", size="7", weight="bold"
        ),
        align="center",
        justify="start",
        padding_x="0.5rem",
        width="100%",
    )
    
    return rx.box(
        rx.vstack(
            header,
            accordion(),
            spacing="5",
            # position="fixed",
            # left="0px",
            # top="0px",
            # z_index="5",
            padding_x="1em",
            padding_y="1.5em",
            bg=rx.color("accent", 3),
            align="start",
            height="100vh",
            # height="650px",
            width="15vw",
        ),
    )