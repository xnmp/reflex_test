import reflex as rx

class Complaint(rx.Model,table=True):
    CASE_RECV_S: str
    pdct_catg_x: str
    pdct_sub_catg_x: str
    CAUS_CATG_X: str
    CAUS_SUB_CATG_X: str
    CASE_SUMY_X: str
    State: str
    case_sumy_length: str
    case_sumy_x_cleaned: str

