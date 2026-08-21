import os
import json
import time
import google.generativeai as genai
from config import Config
from services.whisper_service import transcribe_audio_file_local

def get_gemini_api_key():
    return os.environ.get("GEMINI_API_KEY") or Config.GEMINI_API_KEY

def transcribe_audio_file(audio_path):
    """
    Transcribes audio recording using local faster-whisper (high speed & accuracy, zero API cost).
    Falls back to Gemini API if local model is unavailable.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio recording file not found at: {audio_path}")

    # Primary: Local Faster-Whisper
    try:
        print(f">> [Transcription Pipeline] Transcribing via Local Faster-Whisper...")
        transcript = transcribe_audio_file_local(audio_path, model_size="base")
        if transcript and transcript != "No audible speech detected in recording.":
            return transcript
    except Exception as wErr:
        print(f">> [Local Faster-Whisper Notice]: {wErr}. Attempting Gemini fallback...")

    # Fallback: Google Gemini
    api_key = get_gemini_api_key()
    if not api_key:
        return transcript if 'transcript' in locals() and transcript else "No audible speech detected in recording."

    genai.configure(api_key=api_key, transport='rest')

    try:
        file_size = os.path.getsize(audio_path)
        if file_size < 100:
            return "No audible speech detected in recording (empty audio payload)."

        mime_type = "audio/webm"
        if audio_path.endswith(".wav"):
            mime_type = "audio/wav"
        elif audio_path.endswith(".mp3"):
            mime_type = "audio/mp3"
        elif audio_path.endswith(".ogg"):
            mime_type = "audio/ogg"

        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()

        prompt = (
            "Please transcribe the following audio recording verbatim. "
            "Identify speakers where possible (e.g. Speaker 1, Speaker 2, or by name if mentioned). "
            "Do not add commentary, hallucinations, or summaries—only return the accurate spoken words."
        )

        audio_part = {
            "mime_type": mime_type,
            "data": audio_bytes
        }

        candidate_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        response = None
        last_err = None

        for m_name in candidate_models:
            try:
                print(f">> [Gemini API] Sending audio bytes to '{m_name}'...")
                model = genai.GenerativeModel(model_name=m_name)
                response = model.generate_content([audio_part, prompt])
                if response and response.text:
                    print(f">> [Gemini Transcription Success with '{m_name}']")
                    break
            except Exception as err:
                last_err = err
                continue

        if not response or not response.text:
            if last_err:
                raise last_err
            return "No audible speech detected in recording."

        return response.text.strip()

    except Exception as e:
        print(f">> [Gemini Fallback Transcription Error]: {e}")
        return "No audible speech detected in recording."

def analyze_meeting_transcript(transcript, meeting_title="Meeting", team_members_names=None):
    """
    Analyzes meeting transcript using Google Gemini API with strict structured JSON output.
    Extracts summary, key points, decisions, tasks, risks, and effectiveness score.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("Google Gemini API key is missing. Please set GEMINI_API_KEY in backend/.env to enable AI analysis.")

    if not transcript or not transcript.strip():
        return {
            "summary": "No transcript available for analysis.",
            "key_points": [],
            "decisions": [],
            "tasks": [],
            "risks": [],
            "effectiveness_score": 0.0,
            "next_meeting_date": "Not Mentioned"
        }

    genai.configure(api_key=api_key, transport='rest')

    members_str = ", ".join(team_members_names) if team_members_names else "Team Members"

    prompt = f"""You are an expert AI meeting analyst for a team productivity application.
Analyze the following meeting transcript and extract structured intelligence.

Meeting Title: {meeting_title}
Team Members Roster: {members_str}

TRANSCRIPT:
{transcript}

CRITICAL RULES:
1. ONLY extract information and action items explicitly discussed in the transcript.
2. NEVER invent, fabricate, or hallucinate decisions, tasks, or names that were not spoken.
3. If a specific detail (like deadline, reason, or duration) was not discussed, return 'Not Mentioned'.
4. Calculate an 'effectiveness_score' (float from 1.0 to 10.0) based on meeting clarity, actionable outcomes, and focus.
5. Return ONLY a valid, parseable JSON object matching this exact schema:

{{
  "summary": "Executive summary of the discussion and outcomes (2-4 sentences)",
  "key_points": [
    "Key discussion takeaway 1",
    "Key discussion takeaway 2"
  ],
  "decisions": [
    {{
      "decision_text": "Clear description of the agreed decision",
      "reason": "Rationale discussed during meeting, or 'Not Mentioned'"
    }}
  ],
  "tasks": [
    {{
      "title": "Clear action item title",
      "description": "Specific task instructions discussed",
      "assigned_to_name": "Name of assigned person, or 'Not Mentioned'",
      "priority": "Low | Medium | High | Urgent",
      "deadline": "YYYY-MM-DD or 'Not Mentioned'",
      "estimated_duration": "Estimated time (e.g. 2 hours, 1 day) or 'Not Mentioned'"
    }}
  ],
  "risks": [
    "Identified risk or bottleneck (or 'None mentioned')"
  ],
  "effectiveness_score": 8.5,
  "next_meeting_date": "YYYY-MM-DD or 'Not Mentioned'"
}}
"""

    try:
        candidate_models = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-3.7-flash"]
        response = None
        last_err = None

        for m_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    break
            except Exception as e:
                last_err = e
                continue

        if not response or not response.text:
            raise last_err or RuntimeError("No response from Gemini models.")
        text_content = response.text.strip()
        
        if text_content.startswith("```json"):
            text_content = text_content[7:]
        if text_content.startswith("```"):
            text_content = text_content[3:]
        if text_content.endswith("```"):
            text_content = text_content[:-3]
            
        data = json.loads(text_content.strip())
        return data

    except Exception as e:
        print(f">> [Gemini API Error during Analysis]: {e}")
        raise RuntimeError(f"Gemini Analysis Error: {str(e)}")
