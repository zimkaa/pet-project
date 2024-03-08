from __future__ import annotations
import pickle
from pathlib import Path
from typing import Literal
from typing import TypeAlias

from fastapi import APIRouter
from fastui import AnyComponent
from fastui import FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import PageEvent

from .shared import demo_page


router = APIRouter()

FormKind: TypeAlias = Literal["default"]


@router.get("/{loguru}", response_model=FastUI, response_model_exclude_none=True)
def forms_view(loguru: FormKind) -> list[AnyComponent]:
    # markdown = """
    # text
    # """
    return demo_page(
        # c.Markdown(text=markdown),  # noqa: ERA001
        c.ServerLoad(
            path="/inventory/content/{kind}",
            load_trigger=PageEvent(name="change-form"),
            components=form_content(loguru),
        ),
    )


# class LoginForm(BaseModel):
#     cookie: str = Field(title="Cookie", description="insert cookie")  # noqa: ERA001
#     login: str = Field(title="Login", description="insert login")  # noqa: ERA001
#     password: SecretStr = Field(description="insert password")  # noqa: ERA001
#     proxy_ip: str = Field(title="Ip", description="insert ip")  # noqa: ERA001
#     proxy_port: str = Field(title="Port", description="insert port")  # noqa: ERA001
#     proxy_log: str = Field(title="proxy log", description="insert password")  # noqa: ERA001
#     proxy_pass: SecretStr = Field(description="insert password")  # noqa: ERA001


# def read_file(file_path: str) -> str:
#     with Path(file_path).open() as file:
#         return file.read()  # noqa: ERA001


@router.get("/content/{kind}", response_model=FastUI, response_model_exclude_none=True)
def form_content(kind: FormKind) -> list[AnyComponent]:
    # read_file("tests_files/result.txt")  # noqa: ERA001
    with Path("items.pkl").open("rb") as file:
        items = pickle.load(file)  # noqa: S301
    # items = pickle.load(open("items.pkl", "rb"))  # noqa: ERA001
    match kind:
        case "default":
            # return [
            #     # c.ModelForm(model=LoginForm, display_mode="page", submit_url="/api/inventory/default"),  # noqa: ERA001, E501
            #     c.Markdown(text=text),  # noqa: ERA001
            # ]  # noqa: ERA001, RUF100
            return demo_page(
                c.Table(
                    data=items,
                    columns=[
                        # DisplayLookup(field="name", on_click=GoToEvent(url="/table/users/{id}/")),  # noqa: ERA001
                        DisplayLookup(field="name"),
                        DisplayLookup(field="count"),
                    ],
                ),
            )
        case _:
            msg = f"Invalid kind {kind!r}"
            raise ValueError(msg)
