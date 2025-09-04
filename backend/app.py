# ==============================================================================
# CertifyAI Backend Server
# File: app.py
# ==============================================================================

# --- Step 1: Import necessary libraries ---
# Flask is for creating our web server.
# request lets us handle incoming data (like the document text).
# jsonify formats our output as JSON, a standard for APIs.
# json is a built-in Python library to work with JSON data.
import json
import vertexai
from flask import Flask, request, jsonify
from vertexai.generative_models import GenerativeModel

# --- Step 2: Initialize the Flask App and Vertex AI ---
app = Flask(__name__)

# IMPORTANT: Replace these placeholders with your actual Google Cloud
# project details. You can find your Project ID on the main dashboard
# of the Google Cloud Console. Location can be something like
# "us-central1" or "asia-south1".
PROJECT_ID = "certify-ai-hackathon"  # <-- REPLACE WITH YOUR PROJECT ID
LOCATION = "asia-south1"             # <-- REPLACE WITH YOUR GCP REGION

# Initialize the Vertex AI SDK with your project details.
# This connects our code to your Google Cloud project.
vertexai.init(project=PROJECT_ID, location=LOCATION)


# --- Step 3: Define the Core AI Logic Function ---
def analyze_document_with_gemini(document_text: str) -> str:
    """
    Sends the document text to the Gemini model and returns
    a structured JSON analysis.

    Args:
        document_text: The full text of the legal document to be analyzed.

    Returns:
        A string, which should be the JSON analysis from the model.
    """
    # Load the specific Gemini model we want to use.
    model = GenerativeModel("gemini-1.0-pro")

    # This is our "Master Prompt". It's the most critical part.
    # We instruct the AI on its role, the task, and the EXACT format.
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

    # Send the combined prompt and document text to the model.
    response = model.generate_content(prompt)

    # Return the text part of the model's response.
    return response.text


# --- Step 4: Create the API Endpoints ---

@app.route('/', methods=['GET'])
def health_check():
    """
    Simple health check endpoint to confirm the backend is running.
    """
    return jsonify({
        "status": "healthy",
        "message": "CertifyAI backend is running."
    })


@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """
    Receives document text, passes it to the Gemini function,
    and returns the analysis.
    """
    # Get the JSON data sent from the frontend.
    data = request.get_json()

    # Basic error handling
    if not data or 'text' not in data:
        return jsonify({
            "error": "Invalid request: 'text' field is missing."
        }), 400

    document_text = data['text']

    try:
        # Call our core function to get the analysis from Gemini.
        analysis_result_text = analyze_document_with_gemini(
            document_text
        )

        # Convert model string output into JSON
        analysis_json = json.loads(analysis_result_text)

        # Send the clean JSON object back to the frontend.
        return jsonify(analysis_json)

    except Exception as e:
        # Handle issues like malformed JSON or API failure
        print(f"An error occurred: {e}")
        return jsonify({
            "error": "Failed to analyze document.",
            "details": str(e)
        }), 500


# --- Step 5: Run the Application ---
if __name__ == '__main__':
    # debug=True reloads the server when you save the file.
    app.run(debug=True, port=5000)

