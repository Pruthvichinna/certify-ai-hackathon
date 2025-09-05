# ==============================================================================
# CertifyAI Agent - Step 3 (Final Version)
# File: agent.py
# Description: This file contains the core "brain" of our AI agent.
#              It uses the native Function Calling feature of the Gemini
#              model to define and use tools.
# ==============================================================================

# --- Imports ---
import json
import vertexai
from google.cloud import firestore

# Import the correct classes for defining tools from the Vertex AI SDK
from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    Part,
    FunctionDeclaration,
)

# --- Initialization ---
# Replace 'your-gcp-project-id' with your actual Project ID
PROJECT_ID = "certify-ai-hackathon"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)
db = firestore.Client(project=PROJECT_ID)
model = GenerativeModel("gemini-2.5-pro")


# --- Python Functions for our Tools ---
# These are the regular Python functions that perform the actions.
def save_analysis_to_vault(user_id: str, analysis_data: str) -> str:
    """
    Saves the analysis JSON string to a Firestore database for a
    specific user.
    """
    try:
        data_dict = json.loads(analysis_data)
        collection_ref = db.collection("users", user_id, "analyses")
        update_time, doc_ref = collection_ref.add(data_dict)
        print(
            f"Analysis saved to Firestore with document ID: {doc_ref.id}"
        )
        return (
            f"Successfully saved analysis with document ID: {doc_ref.id}"
        )
    except Exception as e:
        print(f"Error saving to Firestore: {e}")
        return f"Error: Could not save the analysis. Details: {e}"


def schedule_follow_up_event(summary: str, description: str,
                             date: str) -> str:
    """Schedules a follow-up event in the user's calendar."""
    print(f"Calendar tool called for date: {date}")
    # Placeholder: OAuth calendar integration requires a frontend.
    return (
        f"Confirmation: An event named '{summary}' "
        f"was scheduled for {date}."
    )


# --- Tool Configuration ---
# Explicitly tell Gemini which tools it has available.
tool_config = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="save_analysis_to_vault",
            description=(
                "Saves the analysis JSON string to a Firestore database "
                "for a specific user. Use this tool to permanently store "
                "the results of an analysis."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "analysis_data": {"type": "string"},
                },
                "required": ["user_id", "analysis_data"],
            },
        ),
        FunctionDeclaration(
            name="schedule_follow_up_event",
            description=(
                "Schedules a follow-up event in the user's calendar. Use "
                "this tool if the analysis contains important dates or "
                "requires a future action."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["summary", "description", "date"],
            },
        ),
    ]
)


# --- Core Agent Logic ---
def run_analysis_agent(user_id: str, document_text: str) -> dict:
    """Runs the agent workflow using Gemini's native function calling."""
    # === STEP 1: ANALYSIS ===
    print("Agent Step 1: Performing initial document analysis...")
    analysis_prompt = f"""
    You are an expert legal AI assistant. Your purpose is to demystify
    complex legal documents for the average person.

    Carefully review the legal document provided below and return a
    valid JSON object with a "summary" and "risk_analysis".

    Do NOT return any other text, just the JSON. The risk_analysis
    array should contain objects with clause_summary, risk_level,
    explanation, and action_suggestion.

    Legal Document Text:
    ---
    {document_text}
    ---
    """
    analysis_response = model.generate_content(analysis_prompt)
    # Clean the response to remove the markdown wrapper ```json ... ```
    analysis_json_string = (
        analysis_response.text.strip()
        .replace("```json", "")
        .replace("```", "")
    )
    print(f"Agent Step 1 Complete. Analysis: {analysis_json_string}")

    # === STEP 2: REASONING AND TOOL USE ===
    print("Agent Step 2: Reasoning about which tools to use...")
    reasoning_prompt = f"""
    You are an action-oriented agent. Based on the following legal
    analysis, decide which tools to use.

    You MUST ALWAYS use the 'save_analysis_to_vault' tool to store
    the result.

    If the analysis contains any clauses with a 'Red' risk level or
    mentions specific dates, ALSO use the 'schedule_follow_up_event'
    tool.

    Analysis Results:
    ---
    {analysis_json_string}
    ---
    User ID to use for all tools: {user_id}
    """
    response = model.generate_content(
        reasoning_prompt,
        tools=[tool_config],
    )

    # === STEP 3: EXECUTING THE CHOSEN TOOLS ===
    print("Agent Step 3: Executing the tools chosen by the model...")
    actions_taken = []

    for function_call in response.candidates[0].content.parts:
        if not hasattr(function_call, "function_call"):
            continue

        function_name = function_call.function_call.name
        args = {
            key: value
            for key, value in function_call.function_call.args.items()
        }

        print(
            f"Model chose to call function '{function_name}' "
            f"with arguments: {args}"
        )

        if function_name == "save_analysis_to_vault":
            result = save_analysis_to_vault(**args)
            actions_taken.append(result)
        elif function_name == "schedule_follow_up_event":
            result = schedule_follow_up_event(**args)
            actions_taken.append(result)

    print(f"Agent execution complete. Actions taken: {actions_taken}")

    final_result = {
        "analysis": json.loads(analysis_json_string),
        "actions_taken": actions_taken,
    }
    return final_result
