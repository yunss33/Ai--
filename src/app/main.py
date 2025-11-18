from fastapi import FastAPI

from .core.config import get_settings
from .routers import (
    ai,
    announcement,
    assignment,
    auth,
    course,
    schedule,
    user,
)


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, debug=settings.debug)

    application.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    application.include_router(user.router, prefix="/api/user", tags=["user"])
    application.include_router(course.router, prefix="/api", tags=["courses"])
    application.include_router(assignment.router, prefix="/api", tags=["assignments"])
    application.include_router(
        announcement.router,
        prefix="/api",
        tags=["announcements"],
    )
    application.include_router(schedule.router, prefix="/api", tags=["schedule"])
    application.include_router(ai.router, prefix="/api/ai", tags=["ai"])

    return application


app = create_app()
