# FastUI ToDo App

A pure-Python todo application built with FastUI and FastAPI. Manage tasks with add, toggle, and delete actions, filter by status, and enjoy a reactive React-powered UI — all without writing any JavaScript. Ideal for learning FastUI or as a starter template.

## 1 click Deploy

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/fastui-todo-app?referralCode=-Xd4K_&utm_medium=integration&utm_source=template&utm_campaign=generic)

## Dependencies for FastUI ToDo App Hosting

- Python 3.10+
- FastAPI (web framework)
- FastUI >= 0.9.0 (declarative UI components via Pydantic)
- Uvicorn (ASGI server)
- python-multipart (form data parsing)

### mplementation Details

The entire app is a single `app.py`. FastUI components are Pydantic models returned as JSON — the prebuilt React SPA fetches `/api/` routes and renders them automatically:

```python
c.ModelForm(
    model=TodoForm,
    submit_url="/api/add",
    display_mode="inline",
)
```

Forms, tables, navigation, and events are all declared server-side in Python. The catch-all route serves the FastUI React shell:

```python
@app.get("/{path:path}")
def spa_root() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="FastUI Todo"))
```
