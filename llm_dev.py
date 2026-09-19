# # # # from pathlib import Path
# # # # from pypdf import PdfReader

# # # # import os
# # # # from dotenv import load_dotenv
# # # # from io import BytesIO
# # # # import requests
# # # # from elevenlabs.client import ElevenLabs

# # # # # Setup: pip install openai python-dotenv
# # # # # .env file beside this script:  OPENAI_API_KEY=sk-...
# # # # import json
# # # # import os
# # # # from pathlib import Path

# # # # from dotenv import load_dotenv
# # # # from openai import OpenAI


# # # # def extract_text_from_pdf(pdf_path: str | Path) -> str:
# # # #     """Extract and return all text from a PDF as one string."""
# # # #     reader = PdfReader(str(pdf_path))

# # # #     pages = [
# # # #         page.extract_text() or ""
# # # #         for page in reader.pages
# # # #     ]

# # # #     return "\n".join(pages).strip()

# # # # def speech2text(audio_url=None):
    
# # # #     elevenlabs = ElevenLabs(
# # # #     # api_key=API_KEY)
# # # #     api_key="sk_ca1b7902483c483bf603ae4b0ee61ee157849c6889957fd4")
    

# # # #     audio_url = (
# # # #         "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
# # # #     )
# # # #     response = requests.get(audio_url)
# # # #     audio_data = BytesIO(response.content)

# # # #     transcription = elevenlabs.speech_to_text.convert(
# # # #         file=audio_data,
# # # #         model_id="scribe_v2", # Model to use
# # # #         tag_audio_events=True, # Tag audio events like laughter, applause, etc.
# # # #         language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
# # # #         diarize=True, # Whether to annotate who is speaking
# # # #     )

# # # #     return (transcription.text)


# # # # load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

# # # # MODEL = os.getenv("SPLIT_MODEL", "gpt-4.1-nano")

# # # # SCHEMA = {
# # # #     "type": "object",
# # # #     "properties": {"tasks": {"type": "array", "items": {"type": "string"}}},
# # # #     "required": ["tasks"],
# # # #     "additionalProperties": False,   # required by OpenAI strict mode
# # # # }

# # # # SPLIT_PROMPT = """You split a contractor's job description into atomic units of work.

# # # # Rules:
# # # # - One task per object/surface AND per action. "Stain and seal the deck" = 2 tasks.
# # # # - Distribute shared verbs and locations to every item they apply to:
# # # #   "paint the kitchen table, walls and chairs" -> 3 kitchen painting tasks.
# # # # - A new location resets the context: "Also the bathroom sink" belongs to the bathroom, not the kitchen.
# # # # - Format each task as "<location> <object> <action>", lowercase, action as a noun (painting, staining, coating).
# # # # - Only include work actually mentioned. Do not invent tasks.
# # # # - Return {"tasks": []} if there is no work described.

# # # # Example 1:
# # # # Text: "Stain and seal the deck, and pressure wash the fence."
# # # # {"tasks": ["deck staining", "deck sealing", "fence pressure washing"]}

# # # # Example 2:
# # # # Text: "Please repaint the bedroom walls and ceiling. Then the hallway trim needs caulking and painting."
# # # # {"tasks": ["bedroom walls painting", "bedroom ceiling painting", "hallway trim caulking", "hallway trim painting"]}"""

# # # # client = OpenAI(timeout=30.0)  # reads OPENAI_API_KEY from the environment


# # # # def split_tasks(text: str, model: str = MODEL) -> list[str]:
# # # #     """Split free text into a list of atomic work tasks."""
# # # #     if not text or not text.strip():
# # # #         return []

# # # #     resp = client.responses.create(
# # # #         model=model,
# # # #         instructions=SPLIT_PROMPT,
# # # #         input=f"Text: {text.strip()}",
# # # #         text={"format": {
# # # #             "type": "json_schema",
# # # #             "name": "task_list",
# # # #             "schema": SCHEMA,
# # # #             "strict": True,              # output is guaranteed to match SCHEMA
# # # #         }},
# # # #         temperature=0,
# # # #         store=False,
# # # #     )

# # # #     tasks = json.loads(resp.output_text)["tasks"]
# # # #     # Clean up: strip whitespace, drop empties, remove duplicates (keeps order)
# # # #     return list(dict.fromkeys(t.strip().lower() for t in tasks if t.strip()))



# # # # def main():

# # # #     pdf_path = "customer1_estimate.pdf"
# # # #     output = extract_text_from_pdf(pdf_path)
# # # #     print(output)

# # # #     audio_text = speech2text()
# # # #     print(audio_text)

# # # #     sample = (
# # # #         "The customer told me to paint the kitchen table, kitchen walls and chairs. "
# # # #         "Also, the bathroom sink. I also have to coat the garage floor and then do "
# # # #         "the staining and pressure washing for the driveway"
# # # #     )
# # # #     for task in split_tasks(sample):
# # # #         print("-", task)



# # # # if __name__ == "__main__":
# # # #     main()












# # # """ScopeGuard input pipeline helpers.

# # # - extract_text_from_pdf: PDF estimate -> text
# # # - speech_to_text:        audio (file path or URL) -> transcript (ElevenLabs)
# # # - split_tasks:           free text -> list of atomic work tasks (OpenAI)

# # # Setup:
# # #     pip install openai elevenlabs pypdf python-dotenv requests

# # # .env file beside this script:
# # #     OPENAI_API_KEY=sk-...
# # #     ELEVENLABS_API_KEY=sk_...
# # #     SPLIT_MODEL=gpt-4.1-nano        # optional
# # # """

# # # import json
# # # import os
# # # from functools import lru_cache
# # # from io import BytesIO
# # # from pathlib import Path

# # # import requests
# # # from dotenv import load_dotenv
# # # from elevenlabs.client import ElevenLabs
# # # from openai import OpenAI
# # # from pypdf import PdfReader


# # # # ---------------------------------------------------------------------------
# # # # Config
# # # # ---------------------------------------------------------------------------
# # # load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

# # # SPLIT_MODEL = os.getenv("SPLIT_MODEL", "gpt-4.1-nano")
# # # STT_MODEL = "scribe_v2"


# # # def _require_env(name: str) -> str:
# # #     value = os.getenv(name, "").strip()
# # #     if not value:
# # #         raise RuntimeError(f"{name} is not set. Add it to your .env file.")
# # #     return value


# # # # Clients are created on first use, so importing this module never crashes
# # # # just because one of the keys is missing.
# # # @lru_cache(maxsize=1)
# # # def _openai_client() -> OpenAI:
# # #     return OpenAI(api_key=_require_env("OPENAI_API_KEY"), timeout=30.0)


# # # @lru_cache(maxsize=1)
# # # def _elevenlabs_client() -> ElevenLabs:
# # #     return ElevenLabs(api_key=_require_env("ELEVENLABS_API_KEY"))


# # # # ---------------------------------------------------------------------------
# # # # 1. PDF -> text
# # # # ---------------------------------------------------------------------------
# # # def extract_text_from_pdf(pdf_path: str | Path) -> str:
# # #     """Extract and return all text from a PDF as one string."""
# # #     reader = PdfReader(str(pdf_path))
# # #     pages = [page.extract_text() or "" for page in reader.pages]
# # #     return "\n".join(pages).strip()


# # # # ---------------------------------------------------------------------------
# # # # 2. Audio -> text
# # # # ---------------------------------------------------------------------------
# # # def speech_to_text(audio: str | Path) -> str:
# # #     """Transcribe an audio file (local path or http(s) URL) with ElevenLabs."""
# # #     audio = str(audio)
# # #     if audio.startswith(("http://", "https://")):
# # #         response = requests.get(audio, timeout=30)
# # #         response.raise_for_status()
# # #         audio_data = BytesIO(response.content)
# # #     else:
# # #         audio_data = BytesIO(Path(audio).read_bytes())

# # #     transcription = _elevenlabs_client().speech_to_text.convert(
# # #         file=audio_data,
# # #         model_id=STT_MODEL,
# # #         tag_audio_events=True,   # tag laughter, applause, etc.
# # #         language_code="eng",     # None = auto-detect
# # #         diarize=True,            # label who is speaking
# # #     )
# # #     return transcription.text


# # # # ---------------------------------------------------------------------------
# # # # 3. Text -> atomic tasks
# # # # ---------------------------------------------------------------------------
# # # TASKS_SCHEMA = {
# # #     "type": "object",
# # #     "properties": {"tasks": {"type": "array", "items": {"type": "string"}}},
# # #     "required": ["tasks"],
# # #     "additionalProperties": False,  # required by OpenAI strict mode
# # # }

# # # SPLIT_PROMPT = """You split a contractor's job description into atomic units of work.

# # # Rules:
# # # - One task per object/surface AND per action. "Stain and seal the deck" = 2 tasks.
# # # - Distribute shared verbs and locations to every item they apply to:
# # #   "paint the kitchen table, walls and chairs" -> 3 kitchen painting tasks.
# # # - A new location resets the context: "Also the bathroom sink" belongs to the bathroom, not the kitchen.
# # # - Format each task as "<location> <object> <action>", lowercase, action as a noun (painting, staining, coating).
# # # - Only include work actually mentioned. Do not invent tasks.
# # # - Return {"tasks": []} if there is no work described.

# # # Example 1:
# # # Text: "Stain and seal the deck, and pressure wash the fence."
# # # {"tasks": ["deck staining", "deck sealing", "fence pressure washing"]}

# # # Example 2:
# # # Text: "Please repaint the bedroom walls and ceiling. Then the hallway trim needs caulking and painting."
# # # {"tasks": ["bedroom walls painting", "bedroom ceiling painting", "hallway trim caulking", "hallway trim painting"]}"""


# # # def split_tasks(text: str, model: str = SPLIT_MODEL) -> list[str]:
# # #     """Split free text into a list of atomic work tasks."""
# # #     if not text or not text.strip():
# # #         return []

# # #     resp = _openai_client().responses.create(
# # #         model=model,
# # #         instructions=SPLIT_PROMPT,
# # #         input=f"Text: {text.strip()}",
# # #         text={"format": {
# # #             "type": "json_schema",
# # #             "name": "task_list",
# # #             "schema": TASKS_SCHEMA,
# # #             "strict": True,  # output is guaranteed to match the schema
# # #         }},
# # #         temperature=0,       # remove if you switch to a gpt-5 model
# # #         store=False,
# # #     )

# # #     tasks = json.loads(resp.output_text)["tasks"]
# # #     # Strip whitespace, drop empties, remove duplicates (keeps order)
# # #     return list(dict.fromkeys(t.strip().lower() for t in tasks if t.strip()))


# # # # ---------------------------------------------------------------------------
# # # # Demo
# # # # ---------------------------------------------------------------------------
# # # SAMPLE_PDF = "customer1_estimate.pdf"
# # # SAMPLE_AUDIO_URL = "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"
# # # SAMPLE_REQUEST = (
# # #     "The customer told me to paint the kitchen table, kitchen walls and chairs. "
# # #     "Also, the bathroom sink. I also have to coat the garage floor and then do "
# # #     "the staining and pressure washing for the driveway"
# # # )


# # # def main() -> None:
# # #     print("=== PDF estimate ===")
# # #     print(extract_text_from_pdf(SAMPLE_PDF))

# # #     print("\n=== Audio transcript ===")
# # #     print(speech_to_text(SAMPLE_AUDIO_URL))

# # #     print("\n=== Split tasks ===")
# # #     for task in split_tasks(SAMPLE_REQUEST):
# # #         print("-", task)


# # # if __name__ == "__main__":
# # #     main()



























# # """ScopeGuard input pipeline helpers.

# # - extract_text_from_pdf: PDF estimate -> text
# # - speech_to_text:        audio (file path or URL) -> transcript (ElevenLabs)
# # - split_tasks:           free text -> list of atomic work tasks (OpenAI)
# # - compare_requirements:  old text vs new text -> already present / newly added

# # Setup:
# #     pip install openai elevenlabs pypdf python-dotenv requests

# # .env file beside this script:
# #     OPENAI_API_KEY=sk-...
# #     ELEVENLABS_API_KEY=sk_...
# #     SPLIT_MODEL=gpt-4.1-nano        # optional
# # """

# # import json
# # import os
# # from functools import lru_cache
# # from io import BytesIO
# # from pathlib import Path

# # import requests
# # from dotenv import load_dotenv
# # from elevenlabs.client import ElevenLabs
# # from openai import OpenAI
# # from pypdf import PdfReader


# # # ---------------------------------------------------------------------------
# # # Config
# # # ---------------------------------------------------------------------------
# # load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

# # SPLIT_MODEL = os.getenv("SPLIT_MODEL", "gpt-4.1-nano")
# # STT_MODEL = "scribe_v2"


# # def _require_env(name: str) -> str:
# #     value = os.getenv(name, "").strip()
# #     if not value:
# #         raise RuntimeError(f"{name} is not set. Add it to your .env file.")
# #     return value


# # # Clients are created on first use, so importing this module never crashes
# # # just because one of the keys is missing.
# # @lru_cache(maxsize=1)
# # def _openai_client() -> OpenAI:
# #     return OpenAI(api_key=_require_env("OPENAI_API_KEY"), timeout=30.0)


# # @lru_cache(maxsize=1)
# # def _elevenlabs_client() -> ElevenLabs:
# #     return ElevenLabs(api_key=_require_env("ELEVENLABS_API_KEY"))


# # def _ask_json(model: str, instructions: str, user_input: str, name: str, schema: dict) -> dict:
# #     """Call OpenAI and return a dict guaranteed to match `schema`."""
# #     resp = _openai_client().responses.create(
# #         model=model,
# #         instructions=instructions,
# #         input=user_input,
# #         text={"format": {
# #             "type": "json_schema",
# #             "name": name,
# #             "schema": schema,
# #             "strict": True,  # output is guaranteed to match the schema
# #         }},
# #         temperature=0,       # remove if you switch to a gpt-5 model
# #         store=False,
# #     )
# #     return json.loads(resp.output_text)


# # # ---------------------------------------------------------------------------
# # # 1. PDF -> text
# # # ---------------------------------------------------------------------------
# # def extract_text_from_pdf(pdf_path: str | Path) -> str:
# #     """Extract and return all text from a PDF as one string."""
# #     reader = PdfReader(str(pdf_path))
# #     pages = [page.extract_text() or "" for page in reader.pages]
# #     return "\n".join(pages).strip()


# # # ---------------------------------------------------------------------------
# # # 2. Audio -> text
# # # ---------------------------------------------------------------------------
# # def speech_to_text(audio: str | Path) -> str:
# #     """Transcribe an audio file (local path or http(s) URL) with ElevenLabs."""
# #     audio = str(audio)
# #     if audio.startswith(("http://", "https://")):
# #         response = requests.get(audio, timeout=30)
# #         response.raise_for_status()
# #         audio_data = BytesIO(response.content)
# #     else:
# #         audio_data = BytesIO(Path(audio).read_bytes())

# #     transcription = _elevenlabs_client().speech_to_text.convert(
# #         file=audio_data,
# #         model_id=STT_MODEL,
# #         tag_audio_events=True,   # tag laughter, applause, etc.
# #         language_code="eng",     # None = auto-detect
# #         diarize=True,            # label who is speaking
# #     )
# #     return transcription.text


# # # ---------------------------------------------------------------------------
# # # 3. Text -> atomic tasks
# # # ---------------------------------------------------------------------------
# # TASKS_SCHEMA = {
# #     "type": "object",
# #     "properties": {"tasks": {"type": "array", "items": {"type": "string"}}},
# #     "required": ["tasks"],
# #     "additionalProperties": False,
# # }

# # SPLIT_PROMPT = """You split a contractor's job description into atomic units of work.

# # Rules:
# # - One task per object/surface AND per action. "Stain and seal the deck" = 2 tasks.
# # - Distribute shared verbs and locations to every item they apply to:
# #   "paint the kitchen table, walls and chairs" -> 3 kitchen painting tasks.
# # - A new location resets the context: "Also the bathroom sink" belongs to the bathroom, not the kitchen.
# # - Format each task as "<location> <object> <action>", lowercase, action as a noun (painting, staining, coating).
# # - Only include work that WILL be done. Skip work that is explicitly excluded, declined or cancelled
# #   (e.g. "Excluded: hallway painting" -> no task). Ignore prices, dates, names and other non-work text.
# # - Do not invent tasks.
# # - Return {"tasks": []} if there is no work described.

# # Example 1:
# # Text: "Stain and seal the deck, and pressure wash the fence."
# # {"tasks": ["deck staining", "deck sealing", "fence pressure washing"]}

# # Example 2:
# # Text: "Please repaint the bedroom walls and ceiling. Then the hallway trim needs caulking and painting."
# # {"tasks": ["bedroom walls painting", "bedroom ceiling painting", "hallway trim caulking", "hallway trim painting"]}"""


# # def split_tasks(text: str, model: str = SPLIT_MODEL) -> list[str]:
# #     """Split free text into a list of atomic work tasks."""
# #     if not text or not text.strip():
# #         return []

# #     data = _ask_json(model, SPLIT_PROMPT, f"Text: {text.strip()}", "task_list", TASKS_SCHEMA)
# #     # Strip whitespace, drop empties, remove duplicates (keeps order)
# #     return list(dict.fromkeys(t.strip().lower() for t in data["tasks"] if t.strip()))


# # # ---------------------------------------------------------------------------
# # # 4. Old vs new requirements
# # # ---------------------------------------------------------------------------
# # MATCH_SCHEMA = {
# #     "type": "object",
# #     "properties": {
# #         "matches": {
# #             "type": "array",
# #             "items": {
# #                 "type": "object",
# #                 "properties": {
# #                     "new_id": {"type": "integer"},
# #                     "old_id": {"type": ["integer", "null"]},
# #                 },
# #                 "required": ["new_id", "old_id"],
# #                 "additionalProperties": False,
# #             },
# #         }
# #     },
# #     "required": ["matches"],
# #     "additionalProperties": False,
# # }

# # MATCH_PROMPT = """You compare work items.
# # OLD = work already included in the original estimate. NEW = work the customer is requesting now.

# # For EVERY item in NEW, return its new_id and the old_id of the OLD item describing the same work,
# # or null if no OLD item covers it.

# # Same work = same object/surface, same location, same action. Treat wording differences as the same
# # ("repaint kitchen wall" = "kitchen walls painting"). Do NOT match a different location
# # ("hallway walls" != "bedroom walls") or a different action ("deck staining" != "deck sealing").
# # If unsure, use null. Use only IDs that appear in the input."""


# # def _match_new_to_old(new_items: list[str], old_items: list[str], model: str) -> dict[int, int | None]:
# #     """Ask the model which OLD item (if any) each NEW item corresponds to."""
# #     payload = json.dumps({
# #         "OLD": [{"id": i, "task": t} for i, t in enumerate(old_items)],
# #         "NEW": [{"id": i, "task": t} for i, t in enumerate(new_items)],
# #     })
# #     data = _ask_json(model, MATCH_PROMPT, payload, "task_matches", MATCH_SCHEMA)

# #     # Keep only valid IDs. Anything the model skipped or got wrong stays None,
# #     # i.e. it is treated as newly added work (the safe default).
# #     result: dict[int, int | None] = {i: None for i in range(len(new_items))}
# #     for m in data["matches"]:
# #         new_id, old_id = m["new_id"], m["old_id"]
# #         if new_id in result and (old_id is None or 0 <= old_id < len(old_items)):
# #             result[new_id] = old_id
# #     return result


# # def compare_requirements(old_text: str, new_text: str, model: str = SPLIT_MODEL) -> dict:
# #     """Split both texts into atomic tasks and compare new requests with the old scope."""
# #     old_tasks = split_tasks(old_text, model)
# #     new_tasks = split_tasks(new_text, model)

# #     # Exact matches need no LLM call; only send the rest to the model.
# #     unresolved = [t for t in new_tasks if t not in old_tasks]
# #     llm_matches = (
# #         _match_new_to_old(unresolved, old_tasks, model)
# #         if unresolved and old_tasks else {}
# #     )
# #     matched_old = {
# #         task: old_tasks[old_id]
# #         for i, task in enumerate(unresolved)
# #         if (old_id := llm_matches.get(i)) is not None
# #     }

# #     already_present, newly_added = [], []
# #     for task in new_tasks:
# #         if task in old_tasks:
# #             already_present.append({"requested": task, "in_estimate": task})
# #         elif task in matched_old:
# #             already_present.append({"requested": task, "in_estimate": matched_old[task]})
# #         else:
# #             newly_added.append(task)

# #     return {
# #         "old_requirements": old_tasks,
# #         "new_requirements": new_tasks,
# #         "already_present": already_present,
# #         "newly_added": newly_added,
# #         "counts": {
# #             "old_requirements": len(old_tasks),
# #             "new_requirements": len(new_tasks),
# #             "already_present": len(already_present),
# #             "newly_added": len(newly_added),
# #         },
# #     }


# # # ---------------------------------------------------------------------------
# # # Demo
# # # ---------------------------------------------------------------------------
# # SAMPLE_PDF = "customer1_estimate.pdf"
# # SAMPLE_AUDIO_URL = r"C:\Users\dhruv\OneDrive\Documents\Sound Recordings\Recording.m4a"
# # # "https://storage.googleapis.com/eleven-public-cdn/audio/marketing/nicole.mp3"


# # def main() -> None:
# #     old_text = extract_text_from_pdf(SAMPLE_PDF)       # original estimate
# #     new_text = speech_to_text(SAMPLE_AUDIO_URL)        # customer's new request

# #     result = compare_requirements(old_text, new_text)
# #     counts = result["counts"]

# #     print(f"=== Old requirements ({counts['old_requirements']}) ===")
# #     for task in result["old_requirements"]:
# #         print("-", task)

# #     print(f"\n=== New requirements ({counts['new_requirements']}) ===")
# #     for task in result["new_requirements"]:
# #         print("-", task)

# #     print(f"\n=== Already present ({counts['already_present']}) ===")
# #     for item in result["already_present"]:
# #         print(f"- {item['requested']}  (estimate: {item['in_estimate']})")

# #     print(f"\n=== Newly added ({counts['newly_added']}) ===")
# #     for task in result["newly_added"]:
# #         print("-", task)


# # if __name__ == "__main__":
# #     main()
















































# """ScopeGuard input pipeline helpers.

# - extract_text_from_pdf: PDF estimate -> text
# - speech_to_text:        audio (file path or URL) -> transcript (ElevenLabs Scribe v2)
# - live_speech_to_text:   live microphone -> transcript (ElevenLabs Scribe v2 Realtime)
# - split_tasks:           free text -> list of atomic work tasks (OpenAI)
# - compare_requirements:  old text vs new text -> already present / newly added

# Setup:
#     pip install openai elevenlabs pypdf python-dotenv requests sounddevice

# .env file beside this script:
#     OPENAI_API_KEY=sk-...
#     ELEVENLABS_API_KEY=sk_...
#     SPLIT_MODEL=gpt-4.1-nano        # optional

# Usage:
#     python llm_dev.py --pdf customer1_estimate.pdf --audio https://.../request.mp3
#     python llm_dev.py --pdf customer1_estimate.pdf --audio request.m4a
#     python llm_dev.py --pdf customer1_estimate.pdf --mic
# """

# import argparse
# import asyncio
# import base64
# import json
# import os
# from functools import lru_cache
# from io import BytesIO
# from pathlib import Path

# import requests
# from dotenv import load_dotenv
# from elevenlabs.client import ElevenLabs
# from openai import OpenAI
# from pypdf import PdfReader


# # ---------------------------------------------------------------------------
# # Config
# # ---------------------------------------------------------------------------
# load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

# SPLIT_MODEL = os.getenv("SPLIT_MODEL", "gpt-4.1-nano")
# STT_MODEL = "scribe_v2"                    # batch: files and links
# REALTIME_STT_MODEL = "scribe_v2_realtime"  # streaming: live microphone
# MIC_SAMPLE_RATE = 16000                    # Hz, mono, 16-bit PCM
# MIC_CHUNK_SECS = 0.1                       # send audio every 100 ms


# def _require_env(name: str) -> str:
#     value = os.getenv(name, "").strip()
#     if not value:
#         raise RuntimeError(f"{name} is not set. Add it to your .env file.")
#     return value


# # Clients are created on first use, so importing this module never crashes
# # just because one of the keys is missing.
# @lru_cache(maxsize=1)
# def _openai_client() -> OpenAI:
#     return OpenAI(api_key=_require_env("OPENAI_API_KEY"), timeout=30.0)


# @lru_cache(maxsize=1)
# def _elevenlabs_client() -> ElevenLabs:
#     return ElevenLabs(api_key=_require_env("ELEVENLABS_API_KEY"))


# def _ask_json(model: str, instructions: str, user_input: str, name: str, schema: dict) -> dict:
#     """Call OpenAI and return a dict guaranteed to match `schema`."""
#     resp = _openai_client().responses.create(
#         model=model,
#         instructions=instructions,
#         input=user_input,
#         text={"format": {
#             "type": "json_schema",
#             "name": name,
#             "schema": schema,
#             "strict": True,  # output is guaranteed to match the schema
#         }},
#         temperature=0,       # remove if you switch to a gpt-5 model
#         store=False,
#     )
#     return json.loads(resp.output_text)


# # ---------------------------------------------------------------------------
# # 1. PDF -> text
# # ---------------------------------------------------------------------------
# def extract_text_from_pdf(pdf_path: str | Path) -> str:
#     """Extract and return all text from a PDF as one string."""
#     reader = PdfReader(str(pdf_path))
#     pages = [page.extract_text() or "" for page in reader.pages]
#     return "\n".join(pages).strip()


# # ---------------------------------------------------------------------------
# # 2. Audio -> text
# # ---------------------------------------------------------------------------
# def speech_to_text(audio: str | Path) -> str:
#     """Transcribe an audio file (local path or http(s) URL) with ElevenLabs."""
#     audio = str(audio)
#     if audio.startswith(("http://", "https://")):
#         response = requests.get(audio, timeout=30)
#         response.raise_for_status()
#         audio_data = BytesIO(response.content)
#     else:
#         audio_data = BytesIO(Path(audio).read_bytes())

#     transcription = _elevenlabs_client().speech_to_text.convert(
#         file=audio_data,
#         model_id=STT_MODEL,
#         tag_audio_events=True,   # tag laughter, applause, etc.
#         language_code="eng",     # None = auto-detect
#         diarize=True,            # label who is speaking
#     )
#     return transcription.text


# # ---------------------------------------------------------------------------
# # 2b. Live microphone -> text (realtime)
# # ---------------------------------------------------------------------------
# async def _live_speech_to_text_async(language_code: str = "en") -> str:
#     # Imported here so the rest of the module still works on machines without
#     # a mic/PortAudio (e.g. a cloud server) or with an older elevenlabs SDK.
#     import sounddevice as sd
#     from elevenlabs import AudioFormat, CommitStrategy, RealtimeAudioOptions, RealtimeEvents

#     segments: list[str] = []
#     errors: list[str] = []
#     got_commit = asyncio.Event()

#     def on_partial(data: dict) -> None:
#         # Overwrite the same console line while the speaker is mid-sentence.
#         print(f"\r  ... {data.get('text', '')}", end="", flush=True)

#     def on_committed(data: dict) -> None:
#         text = (data.get("text") or "").strip()
#         if text:
#             segments.append(text)
#             print("\r" + " " * 100 + f"\r  > {text}")  # clear the partial line first
#         got_commit.set()

#     def on_error(data: dict) -> None:
#         errors.append(str(data.get("error") or data.get("message") or data))

#     connection = await _elevenlabs_client().speech_to_text.realtime.connect(
#         RealtimeAudioOptions(
#             model_id=REALTIME_STT_MODEL,
#             audio_format=AudioFormat.PCM_16000,
#             sample_rate=MIC_SAMPLE_RATE,
#             commit_strategy=CommitStrategy.VAD,  # server commits on each pause
#             language_code=language_code,
#         )
#     )
#     connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, on_partial)
#     connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, on_committed)
#     connection.on(RealtimeEvents.ERROR, on_error)

#     # The mic callback runs on another thread; hand chunks to the event loop.
#     loop = asyncio.get_running_loop()
#     chunks: asyncio.Queue[bytes] = asyncio.Queue()

#     def on_audio(indata, frames, time_info, status) -> None:
#         loop.call_soon_threadsafe(chunks.put_nowait, bytes(indata))

#     stop = asyncio.ensure_future(asyncio.to_thread(input, "Recording... press Enter to stop.\n"))
#     try:
#         with sd.RawInputStream(
#             samplerate=MIC_SAMPLE_RATE,
#             channels=1,
#             dtype="int16",
#             blocksize=int(MIC_SAMPLE_RATE * MIC_CHUNK_SECS),
#             callback=on_audio,
#         ):
#             while not stop.done() and not errors:
#                 try:
#                     chunk = await asyncio.wait_for(chunks.get(), timeout=0.2)
#                 except asyncio.TimeoutError:
#                     continue
#                 await connection.send({"audio_base_64": base64.b64encode(chunk).decode()})

#         # Flush the last sentence (the speaker may not have paused yet).
#         got_commit.clear()
#         await connection.commit()
#         try:
#             await asyncio.wait_for(got_commit.wait(), timeout=3)
#         except asyncio.TimeoutError:
#             pass
#     finally:
#         await connection.close()

#     if errors and not segments:
#         raise RuntimeError(f"Live transcription failed: {errors[0]}")
#     return " ".join(segments)


# def live_speech_to_text(language_code: str = "en") -> str:
#     """Record from the default microphone until Enter is pressed; return the transcript."""
#     return asyncio.run(_live_speech_to_text_async(language_code))


# # ---------------------------------------------------------------------------
# # 3. Text -> atomic tasks
# # ---------------------------------------------------------------------------
# TASKS_SCHEMA = {
#     "type": "object",
#     "properties": {"tasks": {"type": "array", "items": {"type": "string"}}},
#     "required": ["tasks"],
#     "additionalProperties": False,
# }

# SPLIT_PROMPT = """You split a contractor's job description into atomic units of work.

# Rules:
# - One task per object/surface AND per action. "Stain and seal the deck" = 2 tasks.
# - Distribute shared verbs and locations to every item they apply to:
#   "paint the kitchen table, walls and chairs" -> 3 kitchen painting tasks.
# - A new location resets the context: "Also the bathroom sink" belongs to the bathroom, not the kitchen.
# - Format each task as "<location> <object> <action>", lowercase, action as a noun (painting, staining, coating).
# - Only include work that WILL be done. Skip work that is explicitly excluded, declined or cancelled
#   (e.g. "Excluded: hallway painting" -> no task). Ignore prices, dates, names and other non-work text.
# - Do not invent tasks.
# - Return {"tasks": []} if there is no work described.

# Example 1:
# Text: "Stain and seal the deck, and pressure wash the fence."
# {"tasks": ["deck staining", "deck sealing", "fence pressure washing"]}

# Example 2:
# Text: "Please repaint the bedroom walls and ceiling. Then the hallway trim needs caulking and painting."
# {"tasks": ["bedroom walls painting", "bedroom ceiling painting", "hallway trim caulking", "hallway trim painting"]}"""


# def split_tasks(text: str, model: str = SPLIT_MODEL) -> list[str]:
#     """Split free text into a list of atomic work tasks."""
#     if not text or not text.strip():
#         return []

#     data = _ask_json(model, SPLIT_PROMPT, f"Text: {text.strip()}", "task_list", TASKS_SCHEMA)
#     # Strip whitespace, drop empties, remove duplicates (keeps order)
#     return list(dict.fromkeys(t.strip().lower() for t in data["tasks"] if t.strip()))


# # ---------------------------------------------------------------------------
# # 4. Old vs new requirements
# # ---------------------------------------------------------------------------
# MATCH_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "matches": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "new_id": {"type": "integer"},
#                     "old_id": {"type": ["integer", "null"]},
#                 },
#                 "required": ["new_id", "old_id"],
#                 "additionalProperties": False,
#             },
#         }
#     },
#     "required": ["matches"],
#     "additionalProperties": False,
# }

# MATCH_PROMPT = """You compare work items.
# OLD = work already included in the original estimate. NEW = work the customer is requesting now.

# For EVERY item in NEW, return its new_id and the old_id of the OLD item describing the same work,
# or null if no OLD item covers it.

# Same work = same object/surface, same location, same action. Treat wording differences as the same
# ("repaint kitchen wall" = "kitchen walls painting"). Do NOT match a different location
# ("hallway walls" != "bedroom walls") or a different action ("deck staining" != "deck sealing").
# If unsure, use null. Use only IDs that appear in the input."""


# def _match_new_to_old(new_items: list[str], old_items: list[str], model: str) -> dict[int, int | None]:
#     """Ask the model which OLD item (if any) each NEW item corresponds to."""
#     payload = json.dumps({
#         "OLD": [{"id": i, "task": t} for i, t in enumerate(old_items)],
#         "NEW": [{"id": i, "task": t} for i, t in enumerate(new_items)],
#     })
#     data = _ask_json(model, MATCH_PROMPT, payload, "task_matches", MATCH_SCHEMA)

#     # Keep only valid IDs. Anything the model skipped or got wrong stays None,
#     # i.e. it is treated as newly added work (the safe default).
#     result: dict[int, int | None] = {i: None for i in range(len(new_items))}
#     for m in data["matches"]:
#         new_id, old_id = m["new_id"], m["old_id"]
#         if new_id in result and (old_id is None or 0 <= old_id < len(old_items)):
#             result[new_id] = old_id
#     return result


# def compare_requirements(old_text: str, new_text: str, model: str = SPLIT_MODEL) -> dict:
#     """Split both texts into atomic tasks and compare new requests with the old scope."""
#     old_tasks = split_tasks(old_text, model)
#     new_tasks = split_tasks(new_text, model)

#     # Exact matches need no LLM call; only send the rest to the model.
#     unresolved = [t for t in new_tasks if t not in old_tasks]
#     llm_matches = (
#         _match_new_to_old(unresolved, old_tasks, model)
#         if unresolved and old_tasks else {}
#     )
#     matched_old = {
#         task: old_tasks[old_id]
#         for i, task in enumerate(unresolved)
#         if (old_id := llm_matches.get(i)) is not None
#     }

#     already_present, newly_added = [], []
#     for task in new_tasks:
#         if task in old_tasks:
#             already_present.append({"requested": task, "in_estimate": task})
#         elif task in matched_old:
#             already_present.append({"requested": task, "in_estimate": matched_old[task]})
#         else:
#             newly_added.append(task)

#     return {
#         "old_requirements": old_tasks,
#         "new_requirements": new_tasks,
#         "already_present": already_present,
#         "newly_added": newly_added,
#         "counts": {
#             "old_requirements": len(old_tasks),
#             "new_requirements": len(new_tasks),
#             "already_present": len(already_present),
#             "newly_added": len(newly_added),
#         },
#     }


# # ---------------------------------------------------------------------------s
# # Demo
# # ---------------------------------------------------------------------------
# def main() -> None:
#     parser = argparse.ArgumentParser(description="Compare a new customer request with the original estimate.")
#     parser.add_argument("--pdf", default="customer1_estimate.pdf", help="original estimate PDF")
#     source = parser.add_mutually_exclusive_group(required=True)
#     source.add_argument("--audio", help="audio file path or URL of the new request")
#     source.add_argument("--mic", action="store_true", help="speak the new request live into the microphone")
#     args = parser.parse_args()

#     old_text = extract_text_from_pdf(args.pdf)          # original estimate
#     new_text = live_speech_to_text() if args.mic else speech_to_text(args.audio)

#     print("\n=== Transcript ===")
#     print(new_text or "(nothing transcribed)")
#     print()

#     result = compare_requirements(old_text, new_text)
#     counts = result["counts"]

#     print(f"=== Old requirements ({counts['old_requirements']}) ===")
#     for task in result["old_requirements"]:
#         print("-", task)

#     print(f"\n=== New requirements ({counts['new_requirements']}) ===")
#     for task in result["new_requirements"]:
#         print("-", task)

#     print(f"\n=== Already present ({counts['already_present']}) ===")
#     for item in result["already_present"]:
#         same = item["requested"] == item["in_estimate"]
#         print(f"- {item['requested']}" + ("" if same else f"  (estimate: {item['in_estimate']})"))

#     print(f"\n=== Newly added ({counts['newly_added']}) ===")
#     for task in result["newly_added"]:
#         print("-", task)


# if __name__ == "__main__":
#     main()
















































"""ScopeGuard input pipeline helpers.

- extract_text_from_pdf: PDF estimate -> text
- speech_to_text:        audio (file path or URL) -> transcript (ElevenLabs Scribe v2)
- live_speech_to_text:   live microphone -> transcript (ElevenLabs Scribe v2 Realtime)
- split_tasks:           free text -> list of atomic work tasks (OpenAI)
- compare_requirements:  old text vs new text -> already present / newly added

Setup:
    pip install openai elevenlabs pypdf python-dotenv requests sounddevice

.env file beside this script:
    OPENAI_API_KEY=sk-...
    ELEVENLABS_API_KEY=sk_...
    SPLIT_MODEL=gpt-4.1-nano        # optional

Usage:
    python llm_dev.py --pdf customer1_estimate.pdf --audio https://.../request.mp3
    python llm_dev.py --pdf customer1_estimate.pdf --audio request.m4a
    python llm_dev.py --pdf customer1_estimate.pdf --mic
"""

import argparse
import asyncio
import base64
import json
import os
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from pypdf import PdfReader


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

SPLIT_MODEL = os.getenv("SPLIT_MODEL", "gpt-4.1-nano")
STT_MODEL = "scribe_v2"                    # batch: files and links
REALTIME_STT_MODEL = "scribe_v2_realtime"  # streaming: live microphone
MIC_SAMPLE_RATE = 16000                    # Hz, mono, 16-bit PCM
MIC_CHUNK_SECS = 0.1                       # send audio every 100 ms


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to your .env file.")
    return value


# Clients are created on first use, so importing this module never crashes
# just because one of the keys is missing.
@lru_cache(maxsize=1)
def _openai_client() -> OpenAI:
    return OpenAI(api_key=_require_env("OPENAI_API_KEY"), timeout=30.0)


@lru_cache(maxsize=1)
def _elevenlabs_client() -> ElevenLabs:
    return ElevenLabs(api_key=_require_env("ELEVENLABS_API_KEY"))


def _ask_json(model: str, instructions: str, user_input: str, name: str, schema: dict) -> dict:
    """Call OpenAI and return a dict guaranteed to match `schema`."""
    resp = _openai_client().responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
        text={"format": {
            "type": "json_schema",
            "name": name,
            "schema": schema,
            "strict": True,  # output is guaranteed to match the schema
        }},
        temperature=0,       # remove if you switch to a gpt-5 model
        store=False,
    )
    return json.loads(resp.output_text)


# ---------------------------------------------------------------------------
# 1. PDF -> text
# ---------------------------------------------------------------------------
def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract and return all text from a PDF as one string."""
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


# ---------------------------------------------------------------------------
# 2. Audio -> text
# ---------------------------------------------------------------------------
def speech_to_text(audio: str | Path) -> str:
    """Transcribe an audio file (local path or http(s) URL) with ElevenLabs."""
    audio = str(audio)
    if audio.startswith(("http://", "https://")):
        response = requests.get(audio, timeout=30)
        response.raise_for_status()
        audio_data = BytesIO(response.content)
    else:
        audio_data = BytesIO(Path(audio).read_bytes())

    transcription = _elevenlabs_client().speech_to_text.convert(
        file=audio_data,
        model_id=STT_MODEL,
        tag_audio_events=True,   # tag laughter, applause, etc.
        language_code="eng",     # None = auto-detect
        diarize=True,            # label who is speaking
    )
    return transcription.text


# ---------------------------------------------------------------------------
# 2b. Live microphone -> text (realtime)
# ---------------------------------------------------------------------------
async def _live_speech_to_text_async(language_code: str = "en") -> str:
    # Imported here so the rest of the module still works on machines without
    # a mic/PortAudio (e.g. a cloud server) or with an older elevenlabs SDK.
    import sounddevice as sd
    from elevenlabs import AudioFormat, CommitStrategy, RealtimeAudioOptions, RealtimeEvents

    segments: list[str] = []
    errors: list[str] = []
    got_commit = asyncio.Event()

    def on_partial(data: dict) -> None:
        # Overwrite the same console line while the speaker is mid-sentence.
        print(f"\r  ... {data.get('text', '')}", end="", flush=True)

    def on_committed(data: dict) -> None:
        text = (data.get("text") or "").strip()
        if text:
            segments.append(text)
            print("\r" + " " * 100 + f"\r  > {text}")  # clear the partial line first
        got_commit.set()

    def on_error(data: dict) -> None:
        errors.append(str(data.get("error") or data.get("message") or data))

    connection = await _elevenlabs_client().speech_to_text.realtime.connect(
        RealtimeAudioOptions(
            model_id=REALTIME_STT_MODEL,
            audio_format=AudioFormat.PCM_16000,
            sample_rate=MIC_SAMPLE_RATE,
            commit_strategy=CommitStrategy.VAD,  # server commits on each pause
            language_code=language_code,
        )
    )
    connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, on_partial)
    connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, on_committed)
    connection.on(RealtimeEvents.ERROR, on_error)

    # The mic callback runs on another thread; hand chunks to the event loop.
    loop = asyncio.get_running_loop()
    chunks: asyncio.Queue[bytes] = asyncio.Queue()

    def on_audio(indata, frames, time_info, status) -> None:
        loop.call_soon_threadsafe(chunks.put_nowait, bytes(indata))

    stop = asyncio.ensure_future(asyncio.to_thread(input, "Recording... press Enter to stop.\n"))
    try:
        with sd.RawInputStream(
            samplerate=MIC_SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=int(MIC_SAMPLE_RATE * MIC_CHUNK_SECS),
            callback=on_audio,
        ):
            while not stop.done() and not errors:
                try:
                    chunk = await asyncio.wait_for(chunks.get(), timeout=0.2)
                except asyncio.TimeoutError:
                    continue
                await connection.send({"audio_base_64": base64.b64encode(chunk).decode()})

        # Flush the last sentence (the speaker may not have paused yet).
        got_commit.clear()
        await connection.commit()
        try:
            await asyncio.wait_for(got_commit.wait(), timeout=3)
        except asyncio.TimeoutError:
            pass
    finally:
        await connection.close()

    if errors and not segments:
        raise RuntimeError(f"Live transcription failed: {errors[0]}")
    return " ".join(segments)


def live_speech_to_text(language_code: str = "en") -> str:
    """Record from the default microphone until Enter is pressed; return the transcript."""
    return asyncio.run(_live_speech_to_text_async(language_code))


# ---------------------------------------------------------------------------
# 3. Text -> atomic tasks
# ---------------------------------------------------------------------------
TASKS_SCHEMA = {
    "type": "object",
    "properties": {"tasks": {"type": "array", "items": {"type": "string"}}},
    "required": ["tasks"],
    "additionalProperties": False,
}

SPLIT_PROMPT = """You split a contractor's job description into atomic units of work.

Rules:
- One task per object/surface AND per action. "Stain and seal the deck" = 2 tasks.
- Distribute shared verbs and locations to every item they apply to:
  "paint the kitchen table, walls and chairs" -> 3 kitchen painting tasks.
- A new location resets the context: "Also the bathroom sink" belongs to the bathroom, not the kitchen.
- Format each task as "<location> <object> <action>", lowercase, action as a noun (painting, staining, coating).
- Only include work that WILL be done. Skip work that is explicitly excluded, declined or cancelled
  (e.g. "Excluded: hallway painting" -> no task). Ignore prices, dates, names and other non-work text.
- Do not invent tasks.
- Return {"tasks": []} if there is no work described.

Example 1:
Text: "Stain and seal the deck, and pressure wash the fence."
{"tasks": ["deck staining", "deck sealing", "fence pressure washing"]}

Example 2:
Text: "Please repaint the bedroom walls and ceiling. Then the hallway trim needs caulking and painting."
{"tasks": ["bedroom walls painting", "bedroom ceiling painting", "hallway trim caulking", "hallway trim painting"]}"""


def split_tasks(text: str, model: str = SPLIT_MODEL) -> list[str]:
    """Split free text into a list of atomic work tasks."""
    if not text or not text.strip():
        return []

    data = _ask_json(model, SPLIT_PROMPT, f"Text: {text.strip()}", "task_list", TASKS_SCHEMA)
    # Strip whitespace, drop empties, remove duplicates (keeps order)
    return list(dict.fromkeys(t.strip().lower() for t in data["tasks"] if t.strip()))


# ---------------------------------------------------------------------------
# 4. Old vs new requirements
# ---------------------------------------------------------------------------
MATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "new_id": {"type": "integer"},
                    "old_id": {"type": ["integer", "null"]},
                },
                "required": ["new_id", "old_id"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["matches"],
    "additionalProperties": False,
}

MATCH_PROMPT = """You compare work items.
OLD = work already included in the original estimate. NEW = work the customer is requesting now.

For EVERY item in NEW, return its new_id and the old_id of the OLD item describing the same work,
or null if no OLD item covers it.

Same work = same object/surface, same location, same action. Treat wording differences as the same
("repaint kitchen wall" = "kitchen walls painting"). Do NOT match a different location
("hallway walls" != "bedroom walls") or a different action ("deck staining" != "deck sealing").
If unsure, use null. Use only IDs that appear in the input."""


def _match_new_to_old(new_items: list[str], old_items: list[str], model: str) -> dict[int, int | None]:
    """Ask the model which OLD item (if any) each NEW item corresponds to."""
    payload = json.dumps({
        "OLD": [{"id": i, "task": t} for i, t in enumerate(old_items)],
        "NEW": [{"id": i, "task": t} for i, t in enumerate(new_items)],
    })
    data = _ask_json(model, MATCH_PROMPT, payload, "task_matches", MATCH_SCHEMA)

    # Keep only valid IDs. Anything the model skipped or got wrong stays None,
    # i.e. it is treated as newly added work (the safe default).
    result: dict[int, int | None] = {i: None for i in range(len(new_items))}
    for m in data["matches"]:
        new_id, old_id = m["new_id"], m["old_id"]
        if new_id in result and (old_id is None or 0 <= old_id < len(old_items)):
            result[new_id] = old_id
    return result


def compare_requirements(old_text: str, new_text: str, model: str = SPLIT_MODEL) -> dict:
    """Split both texts into atomic tasks and compare new requests with the old scope."""
    old_tasks = split_tasks(old_text, model)
    new_tasks = split_tasks(new_text, model)

    # Exact matches need no LLM call; only send the rest to the model.
    unresolved = [t for t in new_tasks if t not in old_tasks]
    llm_matches = (
        _match_new_to_old(unresolved, old_tasks, model)
        if unresolved and old_tasks else {}
    )
    matched_old = {
        task: old_tasks[old_id]
        for i, task in enumerate(unresolved)
        if (old_id := llm_matches.get(i)) is not None
    }

    already_present, newly_added = [], []
    for task in new_tasks:
        if task in old_tasks:
            already_present.append({"requested": task, "in_estimate": task})
        elif task in matched_old:
            already_present.append({"requested": task, "in_estimate": matched_old[task]})
        else:
            newly_added.append(task)

    return {
        "old_requirements": old_tasks,
        "new_requirements": new_tasks,
        "already_present": already_present,
        "newly_added": newly_added,
        "counts": {
            "old_requirements": len(old_tasks),
            "new_requirements": len(new_tasks),
            "already_present": len(already_present),
            "newly_added": len(newly_added),
        },
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Compare a new customer request with the original estimate.")
    parser.add_argument("--pdf", default="customer1_estimate.pdf", help="original estimate PDF")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--audio", help="audio file path or URL of the new request")
    source.add_argument("--mic", action="store_true", help="speak the new request live into the microphone")
    args = parser.parse_args()

    old_text = extract_text_from_pdf(args.pdf)          # original estimate
    new_text = live_speech_to_text() if args.mic else speech_to_text(args.audio)

    print("\n=== Transcript ===")
    print(new_text or "(nothing transcribed)")
    print()

    result = compare_requirements(old_text, new_text)
    counts = result["counts"]

    print(f"=== Old requirements ({counts['old_requirements']}) ===")
    for task in result["old_requirements"]:
        print("-", task)

    print(f"\n=== New requirements ({counts['new_requirements']}) ===")
    for task in result["new_requirements"]:
        print("-", task)

    print(f"\n=== Already present ({counts['already_present']}) ===")
    for item in result["already_present"]:
        same = item["requested"] == item["in_estimate"]
        print(f"- {item['requested']}" + ("" if same else f"  (estimate: {item['in_estimate']})"))

    print(f"\n=== Newly added ({counts['newly_added']}) ===")
    for task in result["newly_added"]:
        print("-", task)


if __name__ == "__main__":
    main()