# ==============================================================================
# CertifyAI Web Server - FINAL with Multi-Modal Input
# File: app.py
# Description: This server has endpoints for PDF, Image, and Text analysis.
#              It uses the Cloud Vision API for images.
# ==============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from google.cloud import vision  # Vision API

# Import the main function from agent.py
from agent import run_analysis_agent

app = Flask(__name__)
# Enables Cross-Origin Resource Sharing (CORS) for your frontend
CORS(app)


# --- Helper Function: PDF Text Extraction ---
def extract_text_from_pdf(pdf_file) -> str:
    """Reads a PDF file stream and returns its text content."""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


# --- Helper Function: Image Text Extraction (OCR) ---
def extract_text_from_image(image_file) -> str:
    """
    Reads an image file stream and returns its text content using
    Cloud Vision API.
    """
    try:
        client = vision.ImageAnnotatorClient()
        content = image_file.read()
        image = vision.Image(content=content)

        # Perform text detection (OCR)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            raise Exception(f"{response.error.message}")

        if texts:
            # First annotation is the full detected text
            return texts[0].description
        return ""
    except Exception as e:
        print(f"Error extracting text from Image: {e}")
        return None


@app.route("/", methods=["GET"])
def health_check():
    """Simple endpoint to confirm the server is running."""
    return jsonify({
        "status": "healthy",
        "message": "CertifyAI multi-modal server is running."
    })


# --- API Endpoint for PDF Files ---
@app.route("/analyze-pdf", methods=["POST"])
def analyze_pdf_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith(".pdf"):
        document_text = extract_text_from_pdf(file)
        if document_text is None:
            return jsonify({
                "error": "Could not extract text from the provided PDF."
            }), 500

        user_id = "user_12345_pdf"
        try:
            result = run_analysis_agent(user_id, document_text)
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "error": "The AI agent failed to process the PDF.",
                "details": str(e),
            }), 500
    return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400


# --- API Endpoint for Image Files ---
@app.route("/analyze-image", methods=["POST"])
def analyze_image_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    document_text = extract_text_from_image(file)
    if document_text is None:
        return jsonify({
            "error": "Could not extract text from the image."
        }), 500

    user_id = "user_12345_image"
    try:
        result = run_analysis_agent(user_id, document_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": "The AI agent failed to process the image.",
            "details": str(e),
        }), 500


# --- API Endpoint for Pasted Text ---
@app.route("/analyze-text", methods=["POST"])
def analyze_text_endpoint():
    data = request.get_json()
    if not data or "text" not in data or not data["text"].strip():
        return jsonify({
            "error": "Request must include a non-empty 'text' field."
        }), 400

    document_text = data["text"]
    user_id = "user_12345_text"
    try:
        result = run_analysis_agent(user_id, document_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": "The AI agent failed to process the text.",
            "details": str(e),
        }), 500


if __name__ == "__main__":
    # Port 8080 is common for gunicorn, 5000 for local dev
    app.run(debug=True, port=5000)
