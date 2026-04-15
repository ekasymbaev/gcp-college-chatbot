from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

from src.config import QUESTIONS, CREATOR
from src.utils import build_user_info, validate_user_info

app = FastAPI(title="College Inquiry Chatbot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def load_history(history_json: str):
    if not history_json.strip():
        return []
    try:
        return json.loads(history_json)
    except Exception:
        return []


def dump_history(messages):
    return json.dumps(messages)


def render_index(
    request: Request,
    user_info: dict | None = None,
    errors: dict | None = None,
    form_error: str | None = None,
    status_code: int = status.HTTP_200_OK,
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user_info": user_info or {"first_name": "", "last_name": "", "email": ""},
            "errors": errors or {},
            "form_error": form_error,
        },
        status_code=status_code,
    )


def render_chat(
    request: Request,
    user_info: dict,
    messages: list | None = None,
    chat_error: str | None = None,
    status_code: int = status.HTTP_200_OK,
):
    current_messages = messages or [
        {
            "role": "bot",
            "content": f"Welcome, {user_info['first_name']}. Choose one of the questions below and I will answer it."
        }
    ]

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "user_info": user_info,
            "questions": QUESTIONS,
            "messages": current_messages,
            "history_json": dump_history(current_messages),
            "chat_error": chat_error,
        },
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render_index(request)


@app.post("/start", response_class=HTMLResponse)
async def start_chat(
    request: Request,
    first_name: str = Form(default=""),
    last_name: str = Form(default=""),
    email: str = Form(default=""),
):
    user_info = build_user_info(first_name, last_name, email)
    errors = validate_user_info(user_info)

    if errors:
        return render_index(
            request,
            user_info=user_info,
            errors=errors,
            form_error="Please fill in all fields.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return render_chat(request, user_info=user_info, messages=[])


@app.post("/ask", response_class=HTMLResponse)
async def ask_question(
    request: Request,
    first_name: str = Form(default=""),
    last_name: str = Form(default=""),
    email: str = Form(default=""),
    question_id: str = Form(default=""),
    history_json: str = Form(default=""),
):
    user_info = build_user_info(first_name, last_name, email)
    errors = validate_user_info(user_info)
    messages = load_history(history_json)

    if errors:
        return render_index(
            request,
            user_info=user_info,
            errors=errors,
            form_error="Please enter your information again.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    question = QUESTIONS.get(question_id)
    if question is None:
        return render_chat(
            request,
            user_info=user_info,
            messages=messages,
            chat_error="Please select one of the available questions.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    messages.append({
        "role": "user",
        "content": question["question"]
    })
    messages.append({
        "role": "bot",
        "content": question["answer"]
    })

    return render_chat(
        request,
        user_info=user_info,
        messages=messages,
    )


@app.post("/summary", response_class=HTMLResponse)
async def summary(
    request: Request,
    first_name: str = Form(default=""),
    last_name: str = Form(default=""),
    email: str = Form(default=""),
):
    user_info = build_user_info(first_name, last_name, email)
    errors = validate_user_info(user_info)

    if errors:
        return render_index(
            request,
            user_info=user_info,
            errors=errors,
            form_error="Please provide your information again before viewing the summary.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return templates.TemplateResponse(
        request=request,
        name="summary.html",
        context={
            "user_info": user_info,
            "creator": CREATOR,
        },
        status_code=status.HTTP_200_OK,
    )


@app.get("/summary")
async def summary_redirect():
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)