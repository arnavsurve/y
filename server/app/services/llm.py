from typing import List

from fastapi import File, HTTPException, UploadFile
from google import genai
from google.genai import types
from groq import AsyncGroq

from app.config import settings


async def get_groq_client() -> AsyncGroq:
    return AsyncGroq(api_key=settings.groq_api_key)


async def get_gemini_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


async def extract_text_from_image(
    client: genai.Client, images: List[UploadFile] = File(...)
) -> str | None:
    """
    Uses Google Gemini Vision to extract text from a list of images.
    """
    prompt_contents = []
    prompt_contents.append(
        "Read the text from this/these image(s). If possible, include the platform that you estimate this image originated from at the beginning of your response. Make sure you parse the post or text messages for relevant conversational or post content. Include this in your response. For an image or images withing the screenshot content, describe them in maximum detail."
    )

    for image in images:
        if not image.content_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file {image.filename} has no content type.",
            )

        try:
            image_data = await image.read()
        except Exception as e:
            print("Error reading image data:", e)
            raise HTTPException(status_code=500, detail="Error reading image data")

        try:
            gemini_image_input = types.Part.from_bytes(
                data=image_data,
                mime_type=image.content_type,
            )
            prompt_contents.append(gemini_image_input)
        except Exception as e:
            print("Error calling Gemini API for OCR:", e)
            raise HTTPException(
                status_code=500, detail="Error running OCR on uploaded image"
            )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt_contents,
    )

    print(response.text)

    return response.text if hasattr(response, "text") else "No readable text found."


def format_prompt(
    user_rag_context: List[str], global_rag_context: List[str], query: str
) -> str:
    return f"""
### System Instruction ###
You are an AI assistant that provides helpful, context-aware, and personalized responses.
You will be given:
1. **User-Specific RAG Context**: Information retrieved from the user's own documents.
2. **Global RAG Context**: Knowledge retrieved from external sources.
3. **User Query**: The user's actual request.

Your goal is to generate a response that:
- Prioritizes **User-Specific RAG Context** to ensure personalization and relevance.
- Supplements with **Global RAG Context** if additional information is needed.
- Directly addresses the **User Query** in a **clear, concise, and informative manner**.
- If conflicts exist between **User-Specific** and **Global RAG Context**, prioritize the **User-Specific Context** unless explicitly instructed otherwise.

### User-Specific RAG Context ###
{user_rag_context}

### Global RAG Context ###
{global_rag_context}

### User Query ###
{query}

### Response ###
(Your answer here)
""".strip()


def _format_vibe_check_prompt(
    user_prompt: str | None = "", ocr_text: str | None = ""
) -> str:
    return f"""
### System Instruction ###
You're an expert at social media—but think of yourself as a chill friend giving honest advice, not a robot or formal analyst. You're here to give a casual, authentic "vibe check" to teens and regular social media users. Be straightforward, friendly, and conversational.

Help your audience understand if their content will vibe with people online. Let them know if it’ll get likes, comments, shares, or if it might flop, but keep it cool and relaxed—like chatting with a friend.

Consider:
- **Engagement Potential:** Is it relatable, funny, or interesting enough that people will interact?
- **Emotional Impact:** Does it make people laugh, curious, or get emotional?
- **Clarity & Style:** Is it clear, fun, chill, or catchy enough?
- **Algorithm Friendly:** Does it use the latest trends or hooks to reach more people?
- **Potential Red Flags:** Anything sketchy or risky that could get flagged or make people angry?

Here's what you've got:

Your Text:
{user_prompt if user_prompt else "(No direct user input provided)"}

Text from Images:
{ocr_text if ocr_text else "(No extracted text from images)"}

### Your Vibe Check ###
(Keep your response casual and helpful, pointing out what's good, what's risky, and how they might tweak things to get better results.)
"""


def format_vibe_check_prompt(
    user_prompt: str | None = "", ocr_text: str | None = ""
) -> str:
    return f"""
### System Instruction ###
You're great at social media and SMS vibe checks—like that friend everyone texts before posting or sending a message. Keep your reply short, casual, chill, and friendly. Point out if it'll get likes or flops, highlight anything funny, interesting, or relatable, flag anything risky or sketchy, and suggest tweaks if applicable.

Your Text:
{user_prompt if user_prompt else "(No text provided)"}

Text from Images:
{ocr_text if ocr_text else "(No extracted text from images)"}

### Your Vibe Check ###
(Respond casually and briefly, like you're texting your friend. Point out what's cool, what's sketchy, and how they might boost engagement. Your response should literally be like a text message. 2-3 sentences maximum with minimal punctuation and verbosity. Also, DO NOT use any formatting such as bold or italics. Your response will be presented to the end user in a single or multiple chat bubbles. Mark the end of each bubble with `$endbubble`. DO NOT USE NEWLINES, DO NOT USE `backslash n`, ONLY `$endbubble`. Feel free to use emojis sparingly, and ONLY use emojis popular with the gen-z internet and social media crowd. TRY YOUR ABSOLUTE HARDEST to not sound like an LLM. TRY YOUR ABSOLUTE HARDEST to come across as a real human who is up to date with internet culture, but detached enough to give objective opinions on users' posts or messages. You are cool and laid back, yet always have the user's interests in mind. You are supportive yet not afraid to let bro know if they're tripping. Also feel free to ask a follow up question about the content if something seems unrelated or unfamiliar to you. But do this sparingly and only if it will benefit your understanding of the post.)
""".strip()
