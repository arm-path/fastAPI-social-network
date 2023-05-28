import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PostSchema(BaseModel):
    id: int
    image_path: Optional[str] = None
    text: str
    created: datetime.datetime


class SortedPostSchema(str, Enum):
    descending = 'descending'
    ascending = 'ascending'
