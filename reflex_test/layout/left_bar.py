import reflex as rx

from .instantiate import dropdowns


def accordion() -> rx.Component:
    
    item1 = rx.vstack(
        dropdowns['pdct_catg_x'].element,
        dropdowns['pdct_sub_catg_x'].element,
        rx.text(f"Selected: {dropdowns['pdct_catg_x'].sql_string}"),
        rx.text(f"Selected: {dropdowns['pdct_sub_catg_x'].sql_string}"),
    )
    
    item2 = rx.vstack(
        dropdowns['CAUS_CATG_X'].element,
        dropdowns['CAUS_SUB_CATG_X'].element,
        rx.text(f"Selected: {dropdowns['CAUS_CATG_X'].sql_string}"),
        rx.text(f"Selected: {dropdowns['CAUS_SUB_CATG_X'].sql_string}"),
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