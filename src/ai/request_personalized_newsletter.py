import json
import os
from typing import List

from litellm import completion

from contract_objects.ai_daily_input import RSSEntryEssentials
from contract_objects.newsletter import Newsletter


DEFAULT_MODEL = "gemini/gemini-3.5-flash"

SYSTEM_PROMPT = """Tu es le rédacteur d'une newsletter tech quotidienne et personnelle, publiée sur Discord.
Voici le profil du lecteur, écrit par lui-même. Suis ses préférences de sujets, de format et de langue.

<profil>
{profile}
</profil>

Règles :
- Ne garde que les articles vraiment pertinents pour ce lecteur. Le nombre varie selon les jours : mieux vaut 3 bons articles que 10 moyens.
- Si plusieurs articles parlent du même sujet, fusionne-les en un seul point.
- Regroupe les articles par thème, une section par thème.
- Écris chaque lien en Markdown sous la forme [nom du site](https://...).
- Markdown compatible Discord dans les contenus : gras, italique et liens seulement, pas de titres ni de tableaux.
- N'invente rien qui ne figure pas dans les articles.
- Si le profil contient une section « Personnalité », adopte-la pour le titre, l'intro et la conclusion uniquement.
  Les résumés d'articles restent factuels et clairs. Sans section « Personnalité », garde un ton neutre.

Réponds uniquement avec un objet JSON de cette forme :
{{
  "title": "titre court de l'édition du jour (80 caractères maximum)",
  "intro": "accroche courte (1 à 2 phrases)",
  "sections": [{{"title": "thème", "content": "articles du thème en Markdown"}}],
  "outro": "conclusion courte (1 phrase)"
}}"""


def request_personalized_newsletter(entries: List[RSSEntryEssentials], profile: str) -> Newsletter:
    response = completion(
        model=os.getenv("LLM_MODEL") or DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(profile=profile)},
            {"role": "user", "content": format_entries(entries)},
        ],
        response_format={"type": "json_object"},
        num_retries=3,
    )
    return Newsletter.from_dict(json.loads(response.choices[0].message.content))


def format_entries(entries: List[RSSEntryEssentials]) -> str:
    blocks = []
    for entry in entries:
        lines = [f"Titre : {entry.title}", f"Lien : {entry.link}"]
        if entry.tags:
            lines.append(f"Tags : {', '.join(entry.tags)}")
        text = entry.summary or entry.content
        if text:
            lines.append(f"Résumé : {text}")
        blocks.append("\n".join(lines))
    return "\n\n---\n\n".join(blocks)
