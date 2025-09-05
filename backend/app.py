# ==============================================================================
# CertifyAI Web Server - FINAL VERSION with PDF Upload
# File: app.py
# Description: This server now has two endpoints: one for text and one for
#              PDF file uploads.
# ==============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF library, imported as fitz
import os

# Import the main function from agent.py
from agent import run_analysis_agent

app = Flask(__name__)
# Enables Cross-Origin Resource Sharing for frontend communication
CORS(app)


# --- NEW: Function to extract text from a PDF ---
def extract_text_from_pdf(pdf_file) -> str:
    """Reads a PDF file and returns its text content."""
    try:
        # Open the PDF file directly from the file stream
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


@app.route("/", methods=["GET"])
def health_check():
    """Simple endpoint to check if the server is running."""
    return jsonify({
        "status": "healthy",
        "message": "CertifyAI agent server is running."
    })


# --- NEW: Endpoint for handling PDF file uploads ---
@app.route("/analyze-pdf", methods=["POST"])
def analyze_pdf_endpoint():
    """
    Receives a PDF file, extracts text, and hands it off to the agent.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith(".pdf"):
        document_text = extract_text_from_pdf(file)
        if document_text is None:
            return jsonify({
                "error": "Could not extract text from PDF."
            }), 500

        user_id = "user_12345_pdf_test"  # Placeholder user ID

        try:
            # Call the same agent function as before!
            result = run_analysis_agent(user_id, document_text)
            return jsonify(result)
        except Exception as e:
            print(f"An error occurred in agent processing: {e}")
            return jsonify({
                "error": "Failed to process the document.",
                "details": str(e)
            }), 500
    else:
        return jsonify({
            "error": "Invalid file type. Please upload a PDF."
        }), 400


# We can keep the old text endpoint for testing if we want.
@app.route("/analyze", methods=["POST"])
def analyze_text_endpoint():
    """
    Receives document text and hands it off to the agent orchestrator.
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({
            "error": "Invalid request: 'text' field is missing."
        }), 400

    document_text = data["text"]
    user_id = "user_12345_text_test"

    try:
        result = run_analysis_agent(user_id, document_text)
        return jsonify(result)
    except Exception as e:
        print(f"An error occurred in analyze endpoint: {e}")
        return jsonify({
            "error": "Failed to process the document.",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
