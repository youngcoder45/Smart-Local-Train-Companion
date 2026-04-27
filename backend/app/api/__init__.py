"""
API router package for SLTM backend.

This module marks `app.api` as a package and gives a convenient place to
re-export routers if you choose to centralize registration later.

Current structure:
- Each API module should define: `router = APIRouter(...)`
- The application includes routers from `app.main` (or can include from here).
"""

__all__ = []
