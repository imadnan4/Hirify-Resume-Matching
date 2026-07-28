from app.models.base import Base
import app.models.candidate  # noqa: F401 - register Candidate in Base.metadata
import app.models.job         # noqa: F401 - register JobDescription in Base.metadata
import app.models.match       # noqa: F401 - register Match in Base.metadata
import app.models.resume      # noqa: F401 - register Resume in Base.metadata

__all__ = ["Base"]
