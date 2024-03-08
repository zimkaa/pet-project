from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Literal
from typing import TypeAlias

from fastapi import APIRouter
from fastui import AnyComponent
from fastui import FastUI
from fastui import components as c
from fastui.events import GoToEvent
from fastui.events import PageEvent
from pydantic import BaseModel
from pydantic import Field

from src.scenarios.inventory import get_inventory_client
from src.scenarios.inventory import update_settings
from .shared import demo_page


if TYPE_CHECKING:
    from fastui.forms import fastui_form


router = APIRouter()


# @router.get("/search", response_model=SelectSearchResponse)
# async def search_view(request: Request, q: str) -> SelectSearchResponse:
#     path_ends = f"name/{q}" if q else "all"
#     client: AsyncClient = request.app.state.httpx_client
#     r = await client.get(f"https://restcountries.com/v3.1/{path_ends}")
#     if r.status_code == 404:
#         options = []
#     else:
#         r.raise_for_status()
#         data = r.json()
#         if path_ends == "all":
#             # if we got all, filter to the 20 most populous countries
#             data.sort(key=lambda x: x["population"], reverse=True)
#             data = data[0:20]
#             data.sort(key=lambda x: x["name"]["common"])

#         regions = defaultdict(list)
#         for co in data:
#             regions[co["region"]].append({"value": co["cca3"], "label": co["name"]["common"]})
#         options = [{"label": k, "options": v} for k, v in regions.items()]
#     return SelectSearchResponse(options=options)


FormKind: TypeAlias = Literal["login"]


@router.get("/{kind}", response_model=FastUI, response_model_exclude_none=True)
def forms_view(kind: FormKind) -> list[AnyComponent]:
    # markdown = """
    # text
    # """
    return demo_page(
        # c.Markdown(text=markdown),
        # c.LinkList(
        #     links=[
        #         c.Link(
        #             components=[c.Text(text="Login Form")],
        #             on_click=PageEvent(name="change-form", push_path="/forms/login", context={"kind": "login"}),
        #             active="/forms/login",
        #         ),
        #     ],
        #     mode="tabs",
        #     class_name="+ mb-4",
        # ),
        c.ServerLoad(
            path="/forms/content/{kind}",
            load_trigger=PageEvent(name="change-form"),
            components=form_content(kind),
        ),
    )


@router.get("/content/{kind}", response_model=FastUI, response_model_exclude_none=True)
def form_content(kind: FormKind) -> list[AnyComponent]:
    match kind:
        case "login":
            return [
                c.ModelForm(model=LoginForm, display_mode="page", submit_url="/api/forms/login"),
                # c.ModelForm(model=LoginForm, display_mode="inline", submit_url="/api/forms/login"),
                # c.ModelForm(model=ProxyForm, display_mode="inline", submit_url="/api/forms/login"),
            ]
        case _:
            msg = f"Invalid kind {kind!r}"
            raise ValueError(msg)


class LoginForm(BaseModel):
    cookie: str = Field(title="Cookie", description="insert cookie")
    login: str = Field(title="Login", description="insert login")
    # password: SecretStr = Field(description="insert password")
    password: str = Field(description="insert password")
    proxy_ip: str = Field(title="Ip", description="insert ip")
    proxy_port: str = Field(title="Port", description="insert port")
    proxy_log: str = Field(title="proxy log", description="insert password")
    # proxy_pass: SecretStr = Field(description="insert password")
    proxy_pass: str = Field(description="insert password")


# class ProxyForm(BaseModel):
#     proxy_ip: str = Field(title="Ip", description="insert ip")
#     proxy_port: str = Field(title="Port", description="insert port")
#     proxy_log: str = Field(title="proxy log", description="insert password")
#     proxy_pass: SecretStr = Field(description="insert password")


@router.post("/login", response_model=FastUI, response_model_exclude_none=True)
async def login_form_post(
    form_log: Annotated[LoginForm, fastui_form(LoginForm)],
    # form_prox: Annotated[ProxyForm, fastui_form(ProxyForm)],
) -> list[AnyComponent]:
    update_settings(form_log)
    await get_inventory_client()
    return [c.FireEvent(event=GoToEvent(url="/inventory/default"))]
