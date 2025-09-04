# ==============================================================================
# CertifyAI Backend Server - Step 2 Complete Code
# File: app.py
# Description: This file contains the main backend logic, including the
#              Gemini analysis function and the Firestore Vault Tool.
# ==============================================================================

# --- Step 1: Import all necessary libraries ---
import json
import os
import vertexai
from flask import Flask, request, jsonify

# Google Cloud Firestore for our "Vault Tool"
from google.cloud import firestore

# Gemini AI Model from Vertex AI
from vertexai.generative_models import GenerativeModel

# Google Calendar API libraries for our "Calendar Tool"
# Note: Full implementation of the Calendar Tool requires a frontend.
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime


# --- Step 2: Initialize the Flask App and Google Cloud Services ---
app = Flask(__name__)

# IMPORTANT: Replace these placeholders with your actual
# Google Cloud project details.
PROJECT_ID = "certify-ai-hackathon"   # <-- REPLACE WITH YOUR GCP PROJECT ID
LOCATION = "asia-south1"              # <-- REPLACE WITH YOUR GCP REGION

# Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Firestore Client
db = firestore.Client(project=PROJECT_ID)


# --- Step 3: Define the Core AI Logic Function ---
def analyze_document_with_gemini(document_text: str) -> str:
    """
    Sends the document text to the Gemini model
    and returns a structured JSON analysis.
    """
    model = GenerativeModel("gemini-1.0-pro")

    prompt = f"""
    You are an expert legal AI assistant. Your purpose is to demystify
    complex legal documents for the average person. Carefully review
    the legal document provided below.

    Your task is to return a valid JSON object.
    Do NOT return any other text, just the JSON.

    The JSON object must follow this exact structure:
    {{
      "summary": "Provide a concise, 2-3 sentence summary of the
      document's main purpose and who it is between.",
      "risk_analysis": [
        {{
          "clause_summary": "A brief, simple title for the clause.
          Example: 'Lease Term and Duration'.",
          "risk_level": "Red, Amber, or Green",
          "explanation": "In simple terms, explain what this clause
          means and why it has the assigned risk level.
          'Red' = highly unfavorable or predatory.
          'Amber' = caution or unusual clauses.
          'Green' = standard, fair clauses.",
          "action_suggestion": "Provide a clear, actionable suggestion
          for the user. Example: 'Confirm the termination notice
          period in writing' or 'Set a reminder 60 days before
          this date.'"
        }}
      ]
    }}

    Legal Document Text:
    ---
    {document_text}
    ---
    """

    response = model.generate_content(prompt)
    return response.text


# --- Step 4: Define the Agent's "Tools" ---

# --- TOOL 1: VAULT TOOL (Save to Firestore) ---
def save_analysis_to_vault(user_id: str, analysis_data: dict) -> str:
    """
    Saves the analysis JSON to a Firestore collection for a specific user.
    """
    try:
        # Path: users/{user_id}/analyses
        collection_ref = db.collection("users", user_id, "analyses")
        update_time, doc_ref = collection_ref.add(analysis_data)

        print(
            f"Analysis saved to Firestore "
            f"with document ID: {doc_ref.id}"
        )
        return doc_ref.id
    except Exception as e:
        print(f"Error saving to Firestore: {e}")
        return None


# --- TOOL 2: CALENDAR TOOL (Placeholder) ---
# NOTE: The full calendar tool requires user interaction (login & permission)
# which we will build with the frontend. For now, this is just a placeholder.
def create_calendar_event(summary: str, description: str, event_date: str):
    """
    Placeholder for creating an event in the user's Google Calendar.
    """
    try:
        print(
            "Calendar tool called. In a full app, "
            "this would trigger user authentication."
        )
        # In a real app, you would use Google Calendar API here
        return f"Placeholder: Event '{summary}' would be created for {event_date}."
    except Exception as e:
        print(f"Error with calendar tool placeholder: {e}")
        return None


# --- Step 5: Create the API Endpoints for the Frontend ---

@app.route("/", methods=["GET"])
def health_check():
    """Simple endpoint to check if the server is running."""
    return jsonify({
        "status": "healthy",
        "message": "CertifyAI backend is running."
    })


@app.route("/analyze", methods=["POST"])
def analyze_endpoint():
    """
    Receives document text, runs analysis, saves the result, and returns it.
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({
            "error": "Invalid request: 'text' field is missing."
        }), 400

    document_text = data["text"]
    # In a real app, user_id comes from secure authentication.
    user_id = "user_12345_test"

    try:
        # Get analysis from Gemini
        analysis_result_text = analyze_document_with_gemini(
            document_text
        )
        analysis_json = json.loads(analysis_result_text)

        # Save to Firestore (Vault Tool)
        document_id = save_analysis_to_vault(user_id, analysis_json)

        if document_id:
            analysis_json["vault_document_id"] = document_id

        # Call placeholder Calendar Tool (demo only)
        create_calendar_event(
            "Review Legal Document",
            "Follow up on analyzed document",
            "2025-12-01"
        )

        return jsonify(analysis_json)

    except Exception as e:
        print(f"An error occurred in analyze endpoint: {e}")
        return jsonify({
            "error": "Failed to process the document.",
            "details": str(e)
        }), 500


# --- Step 6: Run the Application ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
