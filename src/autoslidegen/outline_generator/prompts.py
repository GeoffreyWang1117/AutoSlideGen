"""
Prompt templates for LLM outline generation.
"""

SYSTEM_PROMPT = """You are an expert presentation designer and content strategist. Your task is to create well-structured, engaging presentation outlines based on user requirements.

You must generate a JSON object that follows this exact structure:

{
  "metadata": {
    "topic": "string (presentation title, MUST match the user's topic)",
    "audience": "string (target audience)",
    "purpose": "string (presentation purpose)",
    "language": "string (zh/en/ja/es - MUST match user's language)",
    "estimated_duration": "integer (optional, in minutes)"
  },
  "slides": [
    {
      "slide_number": 1,
      "title": "string",
      "slide_type": "title | content | section",
      "bullet_points": [
        {
          "text": "string",
          "level": 1
        }
      ],
      "notes": "string (optional speaker notes)"
    }
  ]
}

CRITICAL slide_type rules:
- "title": ONLY for the first slide (cover page), can have 1-3 bullet points
- "content": For ALL regular content slides with detailed information, MUST have 2-8 bullet points
- "section": ONLY for chapter dividers/transition slides, can have 1-3 bullet points maximum

Key requirements:
1. First slide MUST be type "title" (cover slide)
2. Most slides should be type "content" with 2-8 bullet points each
3. Use "section" type SPARINGLY - only for major chapter transitions (max 2-3 per presentation)
4. Bullet points can have levels 1-3 for hierarchy
5. Ensure logical flow and clear structure
6. Make content presentation-ready, not just notes
7. Each bullet should be concise but complete
8. ALL content (titles, bullets, metadata) MUST be in the user-specified language
9. Output ONLY valid JSON, no other text"""


def get_user_prompt(
    topic: str,
    audience: str,
    purpose: str,
    language: str = "zh",
    num_slides: int = 10,
    bullets_per_slide: int = 4,
    additional_requirements: str = ""
) -> str:
    """
    Generate user prompt for outline creation.

    Args:
        topic: Presentation topic
        audience: Target audience
        purpose: Presentation purpose
        language: Language code
        num_slides: Desired number of slides
        bullets_per_slide: Average bullets per slide
        additional_requirements: Additional requirements

    Returns:
        Formatted user prompt
    """
    language_names = {
        "zh": "中文",
        "en": "English",
        "ja": "日本語",
        "es": "Español"
    }

    prompt = f"""Create a presentation outline with the following specifications:

**Topic**: {topic}
**Target Audience**: {audience}
**Purpose**: {purpose}
**Language**: {language_names.get(language, language)}
**Number of Slides**: {num_slides}
**Average Bullet Points per Slide**: {bullets_per_slide}

"""

    if additional_requirements:
        prompt += f"**Additional Requirements**: {additional_requirements}\n\n"

    prompt += """**Instructions**:
1. Create a compelling title slide that captures attention
2. Structure the presentation with clear sections/chapters if needed
3. Ensure logical progression from introduction to conclusion
4. Make each bullet point actionable and presentation-ready
5. Include speaker notes for key slides where helpful
6. Maintain consistent depth across similar content sections
7. End with a strong conclusion or call-to-action slide

Generate the complete presentation outline as a valid JSON object following the schema provided in the system prompt. Output ONLY the JSON, with no additional commentary or markdown formatting."""

    return prompt


REFINEMENT_PROMPT = """The previous outline had validation errors. Please fix the following issues and regenerate a valid JSON outline:

Errors:
{errors}

Requirements:
1. Address all validation errors listed above
2. Maintain the overall structure and flow
3. Ensure all slides are numbered sequentially starting from 1
4. First slide must be type "title"
5. Content slides must have 2-8 bullet points
6. Output ONLY valid JSON

Generate the corrected outline now:"""


def get_refinement_prompt(errors: str) -> str:
    """
    Generate prompt for refining a failed outline.

    Args:
        errors: Validation error messages

    Returns:
        Refinement prompt
    """
    return REFINEMENT_PROMPT.format(errors=errors)
