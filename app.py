"""
FastUI Todo App — single-file, Railway-ready.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field

# ── Models ────────────────────────────────────────────────────────────

class TodoItem(BaseModel):
    id: str
    title: str
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class TodoForm(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="What needs to be done?")


# ── In-memory store ──────────────────────────────────────────────────

todos: list[TodoItem] = [
    TodoItem(id=str(uuid.uuid4()), title="Learn FastUI basics"),
    TodoItem(id=str(uuid.uuid4()), title="Build a todo app", completed=True),
    TodoItem(id=str(uuid.uuid4()), title="Deploy to Railway"),
]

# ── App ──────────────────────────────────────────────────────────────

app = FastAPI()


def _navbar() -> c.Navbar:
    return c.Navbar(
        title="FastUI Todo",
        title_event=GoToEvent(url="/"),
        start_links=[
            c.Link(
                components=[c.Text(text="All")],
                on_click=GoToEvent(url="/"),
                active="/",
            ),
            c.Link(
                components=[c.Text(text="Active")],
                on_click=GoToEvent(url="/active"),
                active="/active",
            ),
            c.Link(
                components=[c.Text(text="Done")],
                on_click=GoToEvent(url="/done"),
                active="/done",
            ),
        ],
    )


def _todo_page(items: list[TodoItem], heading: str) -> list[AnyComponent]:
    total = len(todos)
    done = sum(1 for t in todos if t.completed)
    active = total - done

    components: list[AnyComponent] = [
        _navbar(),
        c.Page(
            components=[
                c.Heading(text=heading, level=2),
                c.Paragraph(text=f"{total} total · {active} active · {done} done"),
                c.ModelForm(
                    model=TodoForm,
                    submit_url="/api/add",
                    display_mode="inline",
                ),
            ]
        ),
    ]

    if items:
        table_rows = []
        for t in items:
            table_rows.append(
                TodoRow(
                    id=t.id,
                    title=("✅ " if t.completed else "⬜ ") + t.title,
                    created=t.created_at,
                )
            )

        components.append(
            c.Page(
                components=[
                    c.Table(
                        data=table_rows,
                        data_model=TodoRow,
                        columns=[
                            DisplayLookup(
                                field="title",
                                on_click=GoToEvent(url="/toggle/{id}"),
                            ),
                            DisplayLookup(
                                field="created",
                                mode=DisplayMode.datetime,
                            ),
                            DisplayLookup(
                                field="id",
                                title="Delete",
                                on_click=GoToEvent(url="/delete/{id}"),
                            ),
                        ],
                    ),
                ]
            ),
        )
    else:
        components.append(
            c.Page(components=[c.Paragraph(text="🎉 Nothing here!")])
        )

    return components


class TodoRow(BaseModel):
    id: str
    title: str
    created: datetime


# ── API routes ───────────────────────────────────────────────────────

@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def home() -> list[AnyComponent]:
    return _todo_page(todos, "All Todos")


@app.get("/api/active", response_model=FastUI, response_model_exclude_none=True)
def active() -> list[AnyComponent]:
    return _todo_page([t for t in todos if not t.completed], "Active Todos")


@app.get("/api/done", response_model=FastUI, response_model_exclude_none=True)
def done() -> list[AnyComponent]:
    return _todo_page([t for t in todos if t.completed], "Completed Todos")


@app.post("/api/add", response_model=FastUI, response_model_exclude_none=True)
def add_todo(form: Annotated[TodoForm, fastui_form(TodoForm)]) -> list[AnyComponent]:
    todos.insert(0, TodoItem(id=str(uuid.uuid4()), title=form.title))
    return [c.FireEvent(event=GoToEvent(url="/"))]


@app.get("/api/toggle/{todo_id}", response_model=FastUI, response_model_exclude_none=True)
def toggle_todo(todo_id: str) -> list[AnyComponent]:
    for t in todos:
        if t.id == todo_id:
            t.completed = not t.completed
            break
    return [c.FireEvent(event=GoToEvent(url="/"))]


@app.get("/api/delete/{todo_id}", response_model=FastUI, response_model_exclude_none=True)
def delete_todo(todo_id: str) -> list[AnyComponent]:
    global todos
    todos = [t for t in todos if t.id != todo_id]
    return [c.FireEvent(event=GoToEvent(url="/"))]


# ── Catch-all: serve the prebuilt FastUI React SPA ───────────────────

@app.get("/{path:path}")
def spa_root() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="FastUI Todo"))
