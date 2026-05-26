"""Request models for the QueryMind API."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request body for the POST /query endpoint."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Natural language question to query the database",
        examples=["What were the top 5 products by revenue last month?"],
    )
