from dataclasses import dataclass
from typing import List


@dataclass
class NewsletterSection:
     title: str
     content: str


@dataclass
class Newsletter:
     title: str
     intro: str
     sections: List[NewsletterSection]
     outro: str

     @classmethod
     def from_dict(cls, data: dict) -> "Newsletter":
          return cls(
               title=data.get("title", ""),
               intro=data.get("intro", ""),
               sections=[NewsletterSection(s["title"], s["content"]) for s in data.get("sections", [])],
               outro=data.get("outro", ""),
          )

     def to_markdown(self) -> str:
          parts = [f"# {self.title}", self.intro]
          parts += [f"## {section.title}\n{section.content}" for section in self.sections]
          parts.append(self.outro)
          return "\n\n".join(part for part in parts if part)
