import reflex as rx

from .instantiate import dropdowns, taginput_and, taginput_or, taginput_not,date_picker_min, date_picker_max


def accordion() -> rx.Component:
    
    all_dropdowns = rx.vstack(*[dropdown.element for dropdown in dropdowns.values()])
        # rx.text(f"Selected: {dropdowns['pdct_catg_x'].query_args}"),
        # rx.text(f"Selected: {dropdowns['pdct_sub_catg_x'].query_args}"),
        
    keywords = rx.vstack(
        taginput_and.element,
        taginput_or.element,
        taginput_not.element,
    )
    
    dates = rx.vstack(
        date_picker_min.element,
        date_picker_max.element,
    )
    
    return rx.accordion.root(
        rx.accordion.item(
            header="Categorical",
            content=all_dropdowns,
        ),
        rx.accordion.item(
            header="Keywords",
            content=keywords,
        ),
        rx.accordion.item(
            header="Dates",
            content=dates,
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