"""HTML page routes."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request) -> HTMLResponse:
    """Home: dashboard-centric view."""
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request) -> HTMLResponse:
    """Render signup page."""
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/students-page", response_class=HTMLResponse)
def students_page(request: Request) -> HTMLResponse:
    """Students management page."""
    return templates.TemplateResponse("students.html", {"request": request})


@router.get("/departments-page", response_class=HTMLResponse)
def departments_page(request: Request) -> HTMLResponse:
    """Departments management page."""
    return templates.TemplateResponse("departments.html", {"request": request})


@router.get("/subjects-page", response_class=HTMLResponse)
def subjects_page(request: Request) -> HTMLResponse:
    """Subjects management page."""
    return templates.TemplateResponse("subjects.html", {"request": request})


@router.get("/results-page", response_class=HTMLResponse)
def results_page(request: Request) -> HTMLResponse:
    """Results management page."""
    return templates.TemplateResponse("results.html", {"request": request})


@router.get("/fees-page", response_class=HTMLResponse)
def fees_page(request: Request) -> HTMLResponse:
    """Fees management page."""
    return templates.TemplateResponse("fees.html", {"request": request})


@router.get("/clearance-page", response_class=HTMLResponse)
def clearance_page(request: Request) -> HTMLResponse:
    """Clearance management page."""
    return templates.TemplateResponse("clearance.html", {"request": request})


@router.get("/gpa-page", response_class=HTMLResponse)
def gpa_page(request: Request) -> HTMLResponse:
    """GPA Calculator page."""
    return templates.TemplateResponse("gpa.html", {"request": request})


@router.get("/announcements-page", response_class=HTMLResponse)
def announcements_page(request: Request) -> HTMLResponse:
    """Announcements page."""
    return templates.TemplateResponse("announcements.html", {"request": request})


@router.get("/teachers-page", response_class=HTMLResponse)
def teachers_page(request: Request) -> HTMLResponse:
    """Teachers directory page."""
    return templates.TemplateResponse("teachers.html", {"request": request})


@router.get("/profile-page", response_class=HTMLResponse)
def profile_page(request: Request) -> HTMLResponse:
    """User profile page."""
    return templates.TemplateResponse("profile.html", {"request": request})
