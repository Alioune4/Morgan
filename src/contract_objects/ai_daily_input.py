from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from time import mktime

@dataclass
class RSSEntryEssentials:
     id: str
     link: str
     published: datetime
     title: str
     author: Optional[str] = None
     content: Optional[str] = None
     summary: Optional[str] = None
     tags: Optional[List[str]] = None
