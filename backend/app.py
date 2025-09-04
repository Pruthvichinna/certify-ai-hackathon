# ==============================================================================
# CertifyAI Backend Server
# File: app.py
# ==============================================================================

# --- Step 1: Import necessary libraries ---
import json
import vertexai
from flask import Flask, request, jsonify
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore

# New imports for Calendar Tool
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


# --- Step 2: Initialize the Flask App and Vertex AI ---
app = Flask(__name__)

# Replace these placeholders with your actual Google Cloud project details.
PROJECT_ID = "certify-ai-hackathon"  # <-- REPLACE WITH YOUR PROJECT ID
LOCATION = "asia-south1"             # <-- REPLACE WITH YOUR GCP REGION

# Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize the Firestore DB client
db = firestore.Client(project=PROJECT_ID)


# --- Step 3: Define the Core AI Logic Function ---
def analyze_document_with_gemini(document_text: str) -> str:
    """
    Sends the document text to the Gemini model and returns
    a structured JSON analysis.
    """
    model = GenerativeModel("gemini-1.0-pro")

    prompt = f"""
    You are an expert legal AI assistant. Your purpose is to demystify
    complex legal documents for the average person.
    Carefully review the legal document provided below.

    Your task is to return a valid JSON object.
    Do NOT return any other text, just the JSON.
    The JSON object must follow this exact structure:
    {{
      "summary": "Provide a concise, 2-3 sentence summary of the
      document's main purpose and who it is between.",
      "risk_analysis": [
        {{
          "clause_summary": "A brief, simple title for the clause.
          For example: 'Lease Term and Duration'.",
          "risk_level": "Red, Amber, or Green",
          "explanation": "In simple terms, explain what this clause
          means and why it has the assigned risk level.
          'Red' = highly unfavorable or predatory.
          'Amber' = caution or unusual clauses.
          'Green' = standard, fair clauses.",
          "action_suggestion": "Provide a clear, actionable suggestion
          for the user. For example:
          'Confirm the termination notice period in writing' or
          'Set a calendar reminder 60 days before this date.'"
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


# --- TOOL 1: VAULT TOOL (Save to Firestore) ---
def save_analysis_to_vault(user_id: str, analysis_data: dict) -> str:
    """
    Saves the analysis JSON to a Firestore collection for a specific user.
    """
    try:
        # Path: users/{user_id}/analyses
        collection_ref = db.collection('users', user_id, 'analyses')

        # Add a new document with analysis data
        update_time, doc_ref = collection_ref.add(analysis_data)

        print(f"Analysis saved with Firestore ID: {doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        print(f"Error saving to Firestore: {e}")
        return None


# --- TOOL 2: CALENDAR TOOL (Create Google Calendar Event) ---
def create_calendar_event(summary: str, description: str, event_date: str):
    """
    Creates an event in the user's Google Calendar.
    Note: This requires OAuth2 authentication.
    """
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar.events']

        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES,
            redirect_uri='http://localhost:5000/oauth2callback'
        )

        # 🚨 Placeholder for hackathon
        print("Calendar tool called. In a full app, this would trigger user auth.")
        return f"Placeholder: Event '{summary}' would be created for {event_date}."

    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None


# --- Step 4: Create the API Endpoints ---
@app.route('/', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "CertifyAI backend is running."
    })


# This is the main endpoint that our frontend will call.
@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """
    Receives document text, passes it to Gemini,
    saves the result to Firestore, and returns the analysis.
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({
            "error": "Invalid request: 'text' field is missing."
        }), 400

    document_text = data['text']

    # Placeholder user_id (in real app, get from authentication)
    user_id = "user_12345"

    try:
        analysis_result_text = analyze_document_with_gemini(
            document_text
        )
        analysis_json = json.loads(analysis_result_text)

        # --- USE THE VAULT TOOL ---
        document_id = save_analysis_to_vault(user_id, analysis_json)

        if document_id:
            analysis_json['vault_document_id'] = document_id

        return jsonify(analysis_json)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({
            "error": "Failed to analyze document.",
            "details": str(e)
        }), 500


# Demo endpoint for Calendar Tool
@app.route('/calendar-demo', methods=['POST'])
def calendar_demo_endpoint():
    """
    Demo endpoint for Calendar tool.
    Expects: {"summary": "...", "description": "...", "date": "YYYY-MM-DD"}
    """
    data = request.get_json()
    if not data or not all(k in data for k in ("summary", "description", "date")):
        return jsonify({
            "error": "Invalid request: summary, description, and date required"
        }), 400

    result = create_calendar_event(
        data["summary"], data["description"], data["date"]
    )
    return jsonify({"calendar_result": result})


# --- Step 5: Run the Application ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
