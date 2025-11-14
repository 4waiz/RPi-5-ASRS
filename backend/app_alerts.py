import os
import io
import sys


if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


OPENAI_API_KEY = "REMOVED_OPENAI_KEY"

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['OMP_NUM_THREADS'] = '1'

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import openai
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
from typing import Optional, List
import io

# --- API key setup ---
openai.api_key = OPENAI_API_KEY
if not openai.api_key:
    print("=" * 80)
    print("ERROR: OPENAI_API_KEY not set!")
    print("=" * 80)
# ----------------------

MODEL_NAME = 'all-MiniLM-L6-v2'
EXCEL_PATH = 'data/machine_errors.xlsx'

documents = []
doc_embeddings_global = None
model = None
df = None
alerts_data = []

# FMEA Severity Mapping
SEVERITY_LEVELS = {
    'critical': {'priority': 1, 'numeric': 10, 'color': '#D32F2F', 'label': 'Critical'},
    'error': {'priority': 2, 'numeric': 7, 'color': '#FB8C00', 'label': 'Error'},
    'warning': {'priority': 3, 'numeric': 4, 'color': '#F9A825', 'label': 'Warning'}
}

# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    query: str

class SpeechRequest(BaseModel):
    text: str

class QuickAcknowledgeRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

class QuickAcknowledgeResponse(BaseModel):
    acknowledgment: str

class AlertsResponse(BaseModel):
    alerts: List[dict]

class InitialDataResponse(BaseModel):
    diagnosticOptions: List[str]
    alerts: List[dict]
    severityInfo: dict


def calculate_rpn(severity, occurrence, detection):
    """
    Calculate Risk Priority Number (RPN) for FMEA
    RPN = Severity × Occurrence × Detection
    Range: 1-1000 (higher = more critical)
    """
    return severity * occurrence * detection

def assign_occurrence_rating(subsystem, severity_type):
    """
    Occurrence: How often does the failure happen?
    Critical: 6-8, Error: 4-7, Warning: 2-5
    """
    high_occurrence_systems = ['conveyor', 'qc_vision', 'gantry', 'pneumatics']
    medium_occurrence_systems = ['storage', 'elevator', 'plc_network', 'motion']
    
    # Base ranges based on severity
    if severity_type == 'critical':
        base_min, base_max = 6, 8
    elif severity_type == 'error':
        base_min, base_max = 4, 7
    else:  # warning
        base_min, base_max = 2, 5
    
    # Adjust slightly based on subsystem
    if subsystem in high_occurrence_systems:
        return min(10, base_max)
    elif subsystem in medium_occurrence_systems:
        return random.randint(base_min, base_max)
    else:
        return base_min

def assign_detection_rating(detection_source, severity_type):
    """
    Detection: How easily can we detect the failure?
    Critical: 5-8 (harder to detect = more critical)
    Error: 3-6
    Warning: 2-4
    """
    easy_detection = ['plc alarm', 'drive fault', 'sensor diag', 'safety relay']
    moderate_detection = ['hmi script', 'camera', 'operator observation']
    
    # Base ranges based on severity
    if severity_type == 'critical':
        base_min, base_max = 5, 8
    elif severity_type == 'error':
        base_min, base_max = 3, 6
    else:  # warning
        base_min, base_max = 2, 4
    
    if detection_source in easy_detection:
        return base_min
    elif detection_source in moderate_detection:
        return random.randint(base_min, base_max)
    else:
        return base_max

def initialize_rag():
    global documents, doc_embeddings_global, model, df, alerts_data

    print("Initializing RAG pipeline with FMEA...")

    try:
        df = pd.read_excel(EXCEL_PATH, engine='openpyxl').fillna('')
        print(f"✓ Loaded {len(df)} rows from Excel")
    except FileNotFoundError:
        print(f"ERROR: The data file was not found at '{EXCEL_PATH}'.")
        print(f"Please ensure the file exists at: {os.path.abspath(EXCEL_PATH)}")
        print("Creating sample alerts without Excel data...")
        alerts_data = generate_sample_alerts()
        return
    except UnicodeEncodeError as ue:
        print(f"Unicode encoding error (non-critical): {ue}")
        print("Continuing with Excel data despite display issues...")
    except Exception as e:
        print(f"ERROR loading Excel: {str(e).encode('ascii', 'ignore').decode()}")
        alerts_data = generate_sample_alerts()
        return

    for _, row in df.iterrows():
        doc_text = (
            f"Severity: {row['severity']}. "
            f"Symptom: {row['symptom']}. "
            f"Subsystem: {row['subsystem']}. "
            f"Component: {row['component']}. "
            f"Probable Causes: {row['probable_causes']}. "
            f"Quick Checks: {row['quick_checks']}. "
            f"Fix: {row['fix']}. "
            f"Prevent Recurrence: {row['prevent_recurrence']}."
        )
        documents.append(doc_text)

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Creating vector index...")
    doc_embeddings = model.encode(documents, convert_to_tensor=False)
    doc_embeddings_global = doc_embeddings

    doc_embeddings_global = doc_embeddings_global / np.linalg.norm(doc_embeddings_global, axis=1, keepdims=True)

    # Generate alerts from Excel data
    alerts_data = generate_alerts_from_excel()

    print(f"✓ RAG pipeline initialized with {len(alerts_data)} alerts.")
    print(f"Alert severity distribution:")
    critical_count = sum(1 for a in alerts_data if a['severity'] == 'critical')
    error_count = sum(1 for a in alerts_data if a['severity'] == 'error')
    warning_count = sum(1 for a in alerts_data if a['severity'] == 'warning')
    print(f"  Critical: {critical_count}")
    print(f"  Error: {error_count}")
    print(f"  Warning: {warning_count}")


def generate_sample_alerts():
    """Generate sample alerts when Excel file is not available"""
    return [
        {
            "id": 1,
            "machine": "Station A01",
            "title": "Conveyor belt slipping",
            "code": "C101",
            "type": "critical",
            "status": "active",
            "message": "Conveyor belt is slipping",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "subsystem": "conveyor",
            "component": "belt",
            "detection_source": "sensor",
            "severity": "critical",
            "severity_rating": 10,
            "occurrence_rating": 7,
            "detection_rating": 6,
            "rpn": 420,
            "probable_causes": "Belt tension too low",
            "quick_checks": "Check belt tension",
            "fix": "Adjust belt tension",
            "prevent_recurrence": "Regular maintenance"
        }
    ]


def generate_alerts_from_excel():
    """
    Generate realistic alerts from Excel data with FMEA metrics
    """
    global df
    
    if df is None or len(df) == 0:
        return generate_sample_alerts()
    
    alerts = []
    
    # Select 20-25 random rows from Excel to create active alerts
    sample_size = min(108, len(df))
    sampled_rows = df.sample(n=sample_size)
    
    base_time = datetime.now()
    
    print("\n=== Generating Alerts ===")
    
    for idx, (_, row) in enumerate(sampled_rows.iterrows()):
        # CRITICAL: Read severity directly from Excel
        severity_level = str(row['severity']).strip().lower()
        
        # Validate and clean severity from Excel
        if severity_level not in ['critical', 'error', 'warning']:
            print(f"WARNING: Invalid severity '{severity_level}' in Excel row {idx}, defaulting to 'warning'")
            severity_level = 'warning'
        
        alert_type = severity_level  # Use Excel severity directly
        
        # Set status based on severity
        if alert_type == 'critical':
            status = 'active'  # Critical alerts are always active
        elif alert_type == 'error':
            status = 'active' if random.random() > 0.2 else 'resolved'
        else:  # warning
            status = 'active' if random.random() > 0.3 else 'resolved'
        
        # Calculate FMEA metrics - SEVERITY DRIVES THE RPN
        severity_numeric = SEVERITY_LEVELS[alert_type]['numeric']
        occurrence = assign_occurrence_rating(row['subsystem'], alert_type)
        detection = assign_detection_rating(row['detection_source'], alert_type)
        rpn = calculate_rpn(severity_numeric, occurrence, detection)
        
        print(f"Row {idx}: Excel severity='{row['severity']}' -> alert_type='{alert_type}' -> numeric={severity_numeric} -> RPN={rpn}")
        
        # Generate realistic timestamps
        time_offset = timedelta(minutes=random.randint(5, 300))
        alert_time = base_time - time_offset
        
        alert = {
            "id": idx + 1,
            "machine": f"Station {chr(65 + random.randint(0, 4))}{random.randint(1, 10):02d}",
            "title": str(row['symptom'])[:80],
            "code": f"{alert_type[0].upper()}{random.randint(100, 999)}",
            "type": alert_type,  # Legacy field
            "status": status,
            "message": str(row['symptom']),
            "timestamp": alert_time.strftime("%Y-%m-%d %H:%M:%S"),
            "subsystem": str(row['subsystem']),
            "component": str(row['component']),
            "detection_source": str(row['detection_source']),
            
            # FMEA Metrics
            "severity": alert_type,  # This is the key field for filtering!
            "severity_rating": severity_numeric,
            "occurrence_rating": occurrence,
            "detection_rating": detection,
            "rpn": rpn,
            
            # Additional context
            "probable_causes": str(row['probable_causes']),
            "quick_checks": str(row['quick_checks']),
            "fix": str(row['fix']),
            "prevent_recurrence": str(row['prevent_recurrence'])
        }
        
        print(f"Alert {idx+1}: {alert_type.upper()} - RPN:{rpn} - {str(row['symptom'])[:50]}...")
        
        alerts.append(alert)
    
    # Sort by RPN DESCENDING (highest RPN first = most critical)
    alerts.sort(key=lambda x: (-x['rpn'], x['timestamp']))
    
    print(f"\n=== Sorted {len(alerts)} alerts by RPN (highest first) ===")
    print(f"Top 5 RPNs: {[a['rpn'] for a in alerts[:5]]}")
    print(f"Top 5 Severities: {[a['severity'] for a in alerts[:5]]}")
    
    # Validate RPN ranges
    critical_rpns = [a['rpn'] for a in alerts if a['severity'] == 'critical']
    error_rpns = [a['rpn'] for a in alerts if a['severity'] == 'error']
    warning_rpns = [a['rpn'] for a in alerts if a['severity'] == 'warning']
    
    print(f"\nRPN Ranges by Severity:")
    if critical_rpns:
        print(f"  Critical: {min(critical_rpns)} - {max(critical_rpns)} (avg: {sum(critical_rpns)//len(critical_rpns)})")
    if error_rpns:
        print(f"  Error: {min(error_rpns)} - {max(error_rpns)} (avg: {sum(error_rpns)//len(error_rpns)})")
    if warning_rpns:
        print(f"  Warning: {min(warning_rpns)} - {max(warning_rpns)} (avg: {sum(warning_rpns)//len(warning_rpns)})")
    
    return alerts


def retrieve_context(query_text, k=1):
    global doc_embeddings_global, model
    if doc_embeddings_global is None or model is None:
        raise Exception("RAG pipeline not initialized.")

    query_embedding = model.encode([query_text])
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

    similarities = np.dot(doc_embeddings_global, query_embedding.T).flatten()

    indices = np.argsort(similarities)[::-1][:k]

    retrieved_docs = [documents[i] for i in indices]
    return "\n---\n".join(retrieved_docs)


def generate_response(user_query, context):
    if not openai.api_key:
        return "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
    
    # DETECT GREETINGS - handle them separately without technical context
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    user_query_lower = user_query.lower().strip()
    
    is_greeting = any(keyword in user_query_lower for keyword in greeting_keywords)
    
    # If it's just a greeting with no technical content
    if is_greeting and len(user_query.split()) <= 5:
        return "Hello! I'm your ASRS maintenance assistant. I'm here to help you diagnose and troubleshoot any issues with the automated storage and retrieval system. What problem are you experiencing today? You can describe any alarms, unusual sounds, or equipment behavior you've noticed."
    
    system_prompt = """
    You are an expert ASRS (Automated Storage and Retrieval System) maintenance assistant with a friendly, conversational tone.
    You're speaking directly to a technician who needs help, so be natural and supportive like a helpful colleague.

    IMPORTANT: Your response will be converted to speech, so:
    - Speak naturally as if talking to someone, not writing a formal document
    - Use conversational phrases like "Alright, let me help you with that" or "Okay, so here's what I think is happening"
    - Avoid using markdown symbols like ** or # - just speak naturally
    - Don't say "number 1, number 2" - instead say "first", "second", "then"
    - Keep sentences concise and clear for spoken audio
    - Use pauses naturally by ending sentences, not with dashes or special formatting

    Structure your spoken response:
    1. Acknowledge the issue with empathy
    2. Explain what's likely happening in simple terms
    3. Walk them through the steps to fix it conversationally
    4. Mention how to prevent it next time

    Example tone: "Okay, so the conveyor belt issue - I've seen this before. It's usually a tension problem. Here's what you should do first: check if the belt feels loose when you press on it. If it does, you'll need to adjust the tensioner. Let me walk you through it..."
    """

    human_prompt = f"""
    Technician's Query: "{user_query}"

    Context from Past Incidents:
    ---
    {context}
    ---

    Please provide your expert analysis and recommendations based on the instructions.
    """

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt}
            ],
            temperature=0.2,
            max_tokens=400,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Sorry, I encountered an error while generating a response: {str(e)}"


def generate_quick_acknowledgment(user_query):
    """
    Generate a quick, personalized acknowledgment based on the user's query
    This should be FAST (<1 second) and brief (5-10 words)
    """
    if not openai.api_key:
        return "Got it, let me check that for you"
    
    system_prompt = """
    You are a helpful assistant that generates conversational acknowledgments to user queries.

    RULES:
    - Generate a 15-25 word acknowledgment that shows you understood and are investigating
    - Be specific to what they asked about
    - Use natural conversational flow
    - Validate their concern, then say what you're doing
    - DO NOT give solutions yet
    - This will be spoken aloud, so sound natural and helpful

    Examples:
    User: "The conveyor belt is slipping"
    Response: "Got it, I hear you about the conveyor belt slipping. Let me pull up the diagnostic data and check what's going on with that system."

    User: "There's an alarm on the elevator"
    Response: "Understood, the elevator alarm is concerning. Give me a moment to access the system logs and see what triggered it."

    User: "Motor 3 is overheating"
    Response: "Okay, motor 3 overheating - that needs attention. Let me check the temperature sensors and recent operation history real quick."

    Keep it between 15-25 words, sound helpful and engaged.
    """
    
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a brief acknowledgment for: {user_query}"}
            ],
            temperature=0.3,
            max_tokens=60  # Keep it short
        )
        acknowledgment = completion.choices[0].message.content.strip()
        print(f"Quick acknowledgment generated: {acknowledgment}")
        return acknowledgment
    except Exception as e:
        print(f"Error generating acknowledgment: {e}")
        return "Got it, let me check that for you"


def get_diagnostic_options():
    global df
    if df is None: 
        return []
    
    subsystems = df['subsystem'].unique().tolist()
    return subsystems


# Initialize FastAPI app
app = FastAPI(title="ASRS Maintenance Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize RAG
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*80)
    print("Starting FastAPI Backend Server")
    print("="*80)
    print(f"Server will run on: http://localhost:8000")
    print(f"API Endpoints:")
    print(f"  - GET  /api/initial-data")
    print(f"  - POST /api/query")
    print(f"  - POST /api/quick-acknowledge")
    print(f"  - GET  /api/alerts")
    print(f"  - POST /api/synthesize-speech")
    print(f"API Docs available at: http://localhost:8000/docs")
    print("="*80 + "\n")
    initialize_rag()

# Add this after the startup_event function (around line 420)
@app.get('/api/test-openai')
async def test_openai():
    """Test if OpenAI API key is valid"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with a simple TTS request
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="Testing one two three"
        )
        
        return {"status": "success", "message": "OpenAI API key is valid"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# Serve static files (if you have a templates/static directory)
# Uncomment and adjust path as needed
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint - serve your frontend"""
    # If you have an index.html file, return it here
    # For now, returning API info
    return {
        "message": "ASRS Maintenance Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "initial_data": "/api/initial-data",
            "query": "/api/query",
            "quick_acknowledge": "/api/quick-acknowledge",
            "alerts": "/api/alerts",
            "synthesize_speech": "/api/synthesize-speech"
        }
    }


@app.get('/api/initial-data', response_model=InitialDataResponse)
async def get_initial_data():
    """Get initial data including diagnostic options and alerts"""
    diagnostic_options = get_diagnostic_options()
    
    # Add severity levels info for frontend
    severity_info = {
        'levels': SEVERITY_LEVELS,
        'description': 'FMEA-based alert classification with RPN (Risk Priority Number)'
    }
    
    print(f"\n=== API: Sending {len(alerts_data)} alerts to frontend ===")
    
    return {
        "diagnosticOptions": diagnostic_options,
        "alerts": alerts_data,
        "severityInfo": severity_info
    }


@app.post('/api/quick-acknowledge', response_model=QuickAcknowledgeResponse)
async def quick_acknowledge(request: QuickAcknowledgeRequest):
    """
    Generate a quick acknowledgment for the user's query
    This endpoint is designed to be FAST (<1 second)
    """
    user_query = request.query
    
    if not user_query:
        raise HTTPException(status_code=400, detail='Query is required')
    
    print(f"\n=== Quick Acknowledge Request ===")
    print(f"Query: {user_query}")
    
    try:
        acknowledgment = generate_quick_acknowledgment(user_query)
        print(f"Acknowledgment: {acknowledgment}")
        return {"acknowledgment": acknowledgment}
    except Exception as e:
        print(f"Error generating acknowledgment: {e}")
        # Fallback to generic acknowledgment
        return {"acknowledgment": "Got it, let me check that for you"}


@app.post('/api/query', response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle user queries for maintenance assistance"""
    user_query = request.query
    
    if not user_query:
        raise HTTPException(status_code=400, detail='Query is required')
    
    print(f"\n=== Received Voice Query ===")
    print(f"Query: {user_query}")

    try:
        # DETECT GREETINGS - skip RAG retrieval for greetings
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
        user_query_lower = user_query.lower().strip()
        is_greeting = any(keyword in user_query_lower for keyword in greeting_keywords)
        
        # If greeting with no technical content, skip context retrieval
        if is_greeting and len(user_query.split()) <= 5:
            context = ""  # Empty context for greetings
        else:
            context = retrieve_context(user_query)  # Normal RAG retrieval for technical queries
        
        response_text = generate_response(user_query, context)
        
        print(f"Response generated successfully")
        
        return {"response": response_text}
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f'Error processing query: {str(e)}')


@app.get('/api/alerts', response_model=AlertsResponse)
async def get_alerts(filter: str = Query(default='all', description='Filter alerts by type')):
    """Get filtered alerts"""
    
    print(f"\n=== API: Filtering alerts by '{filter}' ===")
    
    filtered_alerts = alerts_data

    if filter == 'critical':
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'critical']
    elif filter == 'error':
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'error']
    elif filter == 'warning':
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'warning']
    elif filter == 'alerts':
        # Legacy support: show critical + error
        filtered_alerts = [a for a in alerts_data if a['severity'] in ['critical', 'error']]
    elif filter == 'warnings':
        # Legacy support
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'warning']
    
    print(f"Returning {len(filtered_alerts)} alerts")

    return {'alerts': filtered_alerts}


@app.post('/api/synthesize-speech')
async def synthesize_speech(request: SpeechRequest):
    """
    Convert text to natural-sounding speech using OpenAI TTS API
    """
    text = request.text
    
    if not text:
        raise HTTPException(status_code=400, detail='Text is required')
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Use OpenAI's TTS with natural voice
        response = client.audio.speech.create(
            model="tts-1",  # Use tts-1-hd for higher quality (but slower)
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            speed=1.0
        )
        
        # Convert to bytes and return as streaming response
        audio_bytes = io.BytesIO(response.content)
        
        return StreamingResponse(
            audio_bytes,
            media_type='audio/mpeg',
            headers={
                'Content-Disposition': 'inline; filename="speech.mp3"'
            }
        )
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=f'Error generating speech: {str(e)}')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )