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
from openai import OpenAI
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
openai_client = OpenAI(api_key=OPENAI_API_KEY)
if not OPENAI_API_KEY:
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

# Semantic caching for AI responses
response_cache = {
    'queries': [],        # List of cached query texts
    'embeddings': None,   # Numpy array of query embeddings
    'responses': [],      # List of cached responses
    'timestamps': []      # List of timestamps for cache management
}
CACHE_SIMILARITY_THRESHOLD = 0.92  # High threshold for accurate matches

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


def retrieve_context(query_text, k=3):
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
    if not OPENAI_API_KEY:
        return "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."

    # DETECT GREETINGS - handle them separately without technical context
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    user_query_lower = user_query.lower().strip()

    is_greeting = any(keyword in user_query_lower for keyword in greeting_keywords)

    # If it's just a greeting with no technical content
    if is_greeting and len(user_query.split()) <= 5:
        return "Hello! I'm your ASRS maintenance assistant. I'm here to help you diagnose and troubleshoot any issues with the automated storage and retrieval system. What problem are you experiencing today? You can describe any alarms, unusual sounds, or equipment behavior you've noticed."

    system_prompt = """
    You are an expert ASRS (Automated Storage and Retrieval System) maintenance assistant with deep knowledge of industrial automation.

    ASRS SYSTEM COMPONENTS YOU KNOW ABOUT:
    - Conveyor System: Motors, belts, encoders (E1), photoeyes (PE1), rollers, drive controllers
    - Elevator/Lift: Motors, cables, brakes, position sensors, limit switches
    - Gantry/Crane: X/Y/Z-axis motors, gripper mechanisms, cable chains
    - Storage Racks: Rack structures, bin sensors, location markers, access doors
    - Safety Systems: Emergency stops, light curtains, interlocks, safety relays
    - PLC/Network: PLC modules, network switches, I/O cards, power supplies
    - QC/Vision: Cameras, barcode scanners, vision processors, lighting systems
    - Pneumatics: Compressors, valves, cylinders, air lines, pressure sensors
    - HMI/Interface: Touch panels, displays, control boards, ethernet cables

    IMPORTANT GUIDELINES:
    - Use your expert knowledge of ASRS systems to diagnose issues, even if not in the provided context
    - Think through the mechanical, electrical, and logical causes based on symptoms
    - If someone describes a noise, analyze which components could make that sound
    - Consider all possible root causes, not just what's in historical logs
    - Your response will be converted to speech, so speak naturally and conversationally
    - Use phrases like "Based on what you're describing" or "That sound typically indicates"
    - Avoid markdown symbols (**, #) - speak naturally instead
    - Say "first", "second", "then" instead of "number 1, number 2"

    Structure your response:
    1. Acknowledge the issue and what it likely indicates
    2. Explain the probable causes with technical reasoning
    3. Provide diagnostic steps and troubleshooting
    4. Include safety warnings and verification procedures
    5. Mention preventive measures

    Example: "Okay, hearing a grinding noise from one of the sensors is actually unusual, because sensors themselves don't typically make noise. Based on your description, I think what you're actually hearing is probably coming from a nearby mechanical component. In ASRS systems, grinding sounds usually point to one of three things: a bearing that's failing in a motor, a misaligned belt or pulley rubbing against its housing, or debris caught in a moving part. Since you mentioned it's near a sensor, I'd check the conveyor motor bearings first - those photoeye sensors are usually mounted close to the conveyor assemblies. Here's what to do: power down the system, then manually rotate the conveyor rollers and motor shafts. Feel for any roughness or hear for grinding. Also inspect around the sensor mounting area for any loose brackets or debris. If the bearing's the issue, you'll need to replace it before it seizes up completely."
    """

    # Build the human prompt with optional context
    context_section = ""
    if context and context.strip():
        context_section = f"""

    Context from Past Incidents (use if relevant, but rely on your expertise first):
    ---
    {context}
    ---
    """

    human_prompt = f"""
    Technician's Query: "{user_query}"
    {context_section}

    Analyze this issue using your expert knowledge of ASRS systems. Consider the symptoms, likely causes, and provide practical troubleshooting steps. Don't just rely on historical data - think through what could mechanically, electrically, or logically cause this problem.
    """

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Much faster than gpt-4o-mini
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt}
            ],
            temperature=0.2,
            max_tokens=400,  # Shorter responses for speed
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Sorry, I encountered an error while generating a response: {str(e)}"


def generate_quick_acknowledgment(user_query):
    """
    Generate a quick, personalized acknowledgment based on the user's query
    This should be INSTANT - no AI call, just pattern matching
    """
    query_lower = user_query.lower()

    # Component/subsystem patterns
    component_patterns = {
        'conveyor': ['conveyor', 'conveyer', 'belt', 'roller'],
        'motor': ['motor', 'drive', 'actuator'],
        'elevator': ['elevator', 'lift', 'hoist'],
        'sensor': ['sensor', 'photoeye', 'photo eye', 'pe1', 'encoder'],
        'gantry': ['gantry', 'crane', 'axis'],
        'gripper': ['gripper', 'grab', 'clamp'],
        'plc': ['plc', 'controller', 'cpu', 'network'],
        'safety': ['safety', 'estop', 'e-stop', 'emergency', 'interlock'],
        'pneumatic': ['pneumatic', 'air', 'compressor', 'valve', 'cylinder'],
        'rack': ['rack', 'storage', 'bin', 'shelf'],
        'hmi': ['hmi', 'screen', 'display', 'panel', 'interface'],
        'power': ['power', 'supply', 'voltage', 'electrical'],
        'communication': ['communication', 'network', 'ethernet', 'cable']
    }

    # Issue type patterns
    issue_patterns = {
        'not working': ['not working', 'broken', 'failed', 'dead', 'stopped'],
        'error': ['error', 'fault', 'alarm', 'warning'],
        'noise': ['noise', 'sound', 'loud', 'grinding', 'squeaking'],
        'slow': ['slow', 'sluggish', 'delayed'],
        'stuck': ['stuck', 'jammed', 'blocked'],
        'overheating': ['hot', 'overheating', 'heat'],
        'vibration': ['vibrating', 'shaking', 'vibration']
    }

    # Find matching component
    detected_component = None
    for component, keywords in component_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_component = component
            break

    # Find matching issue type
    detected_issue = None
    for issue, keywords in issue_patterns.items():
        if any(keyword in query_lower for keyword in keywords):
            detected_issue = issue
            break

    # Generate acknowledgment
    if detected_component and detected_issue:
        return f"Got it, checking {detected_component} {detected_issue}."
    elif detected_component:
        return f"Got it, analyzing {detected_component} issue."
    elif detected_issue:
        return f"Got it, investigating the {detected_issue}."
    else:
        return "Got it, analyzing your report."


def get_diagnostic_options():
    global df
    if df is None:
        return []

    subsystems = df['subsystem'].unique().tolist()
    return subsystems


def check_cache(query):
    """
    Check if we have a cached response for a similar query.
    Returns (cached_response, similarity_score) if found, else (None, 0)
    """
    global response_cache, model

    if not response_cache['queries'] or model is None:
        return None, 0

    # Encode the incoming query
    query_embedding = model.encode([query], convert_to_tensor=False)[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # Calculate similarity with all cached queries
    similarities = np.dot(response_cache['embeddings'], query_embedding)

    # Find the best match
    max_idx = np.argmax(similarities)
    max_similarity = similarities[max_idx]

    print(f"🔍 Cache check: best match similarity = {max_similarity:.3f} (threshold = {CACHE_SIMILARITY_THRESHOLD})")

    if max_similarity >= CACHE_SIMILARITY_THRESHOLD:
        cached_query = response_cache['queries'][max_idx]
        cached_response = response_cache['responses'][max_idx]
        print(f"✅ CACHE HIT! Similar to: '{cached_query}'")
        return cached_response, max_similarity

    print("❌ No cache hit")
    return None, max_similarity


def add_to_cache(query, response):
    """
    Add a new query-response pair to the cache
    """
    global response_cache, model

    if model is None:
        return

    # Encode the query
    query_embedding = model.encode([query], convert_to_tensor=False)[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # Add to cache
    response_cache['queries'].append(query)
    response_cache['responses'].append(response)
    response_cache['timestamps'].append(datetime.now())

    # Update embeddings array
    if response_cache['embeddings'] is None:
        response_cache['embeddings'] = query_embedding.reshape(1, -1)
    else:
        response_cache['embeddings'] = np.vstack([
            response_cache['embeddings'],
            query_embedding.reshape(1, -1)
        ])

    print(f"💾 Added to cache. Total cached queries: {len(response_cache['queries'])}")


def pregenerate_common_queries():
    """
    Pre-generate responses for common maintenance queries.
    This runs on startup to build a knowledge base for instant responses.
    """
    common_queries = [
        # Conveyor issues
        "The conveyor belt is not moving",
        "Conveyor belt is stuck",
        "Conveyor motor is making noise",
        "Belt is slipping on the conveyor",
        "Conveyor rollers are not rotating",

        # Motor issues
        "Motor is overheating",
        "Motor won't start",
        "Motor is running but very slow",
        "Strange noise from the motor",
        "Motor keeps tripping the circuit breaker",

        # Sensor issues
        "Photoeye sensor is not detecting",
        "Encoder is not reading position",
        "Sensor light is not turning on",
        "Position sensor giving wrong readings",

        # Elevator/Lift issues
        "Elevator is not moving",
        "Lift is stuck between floors",
        "Elevator motor making grinding noise",
        "Lift cables are loose",

        # Safety issues
        "Emergency stop is not working",
        "Safety light curtain is triggered",
        "Interlock is preventing operation",

        # PLC/Control issues
        "PLC is not communicating",
        "HMI screen is blank",
        "Control panel is not responding",
        "Network connection lost",

        # Power issues
        "System has no power",
        "Voltage fluctuations",
        "Circuit breaker keeps tripping",
    ]

    print(f"\n🔧 Pre-generating responses for {len(common_queries)} common queries...")
    print("This may take a few minutes but will enable instant responses later.\n")

    for i, query in enumerate(common_queries, 1):
        try:
            print(f"[{i}/{len(common_queries)}] Generating: {query}")

            # Check if already cached
            cached, similarity = check_cache(query)
            if cached and similarity > 0.95:
                print(f"  → Already cached (similarity: {similarity:.3f})")
                continue

            # Generate response using normal RAG pipeline
            context = retrieve_context(query)
            response = generate_response(query, context)

            # Add to cache
            add_to_cache(query, response)
            print(f"  ✅ Cached")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    print(f"\n✅ Pre-generation complete! Cache now contains {len(response_cache['queries'])} queries.\n")


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
    print(f"  - POST /api/query (with semantic caching)")
    print(f"  - POST /api/quick-acknowledge")
    print(f"  - GET  /api/alerts")
    print(f"  - POST /api/synthesize-speech")
    print(f"  - POST /api/cache/pregenerate (Generate cache manually)")
    print(f"  - GET  /api/cache/stats (View cache statistics)")
    print(f"API Docs available at: http://localhost:8000/docs")
    print("="*80 + "\n")
    initialize_rag()

    # Optional: Uncomment the next line to pre-generate cache on startup
    # This will add 2-3 minutes to startup time but enable instant responses
    # pregenerate_common_queries()

# Add this after the startup_event function (around line 420)
@app.get('/api/test-openai')
async def test_openai():
    """Test if OpenAI API key is valid"""
    try:
        # Test with a simple TTS request
        response = openai_client.audio.speech.create(
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


@app.post('/api/cache/pregenerate')
async def trigger_pregeneration():
    """
    Manually trigger pre-generation of common query responses.
    This will take a few minutes but will enable instant responses for common queries.
    """
    try:
        pregenerate_common_queries()
        return {
            "message": "Cache pre-generation completed",
            "total_cached": len(response_cache['queries'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error pre-generating cache: {str(e)}')


@app.get('/api/cache/stats')
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "total_cached_queries": len(response_cache['queries']),
        "cache_threshold": CACHE_SIMILARITY_THRESHOLD,
        "sample_queries": response_cache['queries'][:5] if response_cache['queries'] else []
    }


@app.post('/api/query', response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle user queries for maintenance assistance"""
    user_query = request.query

    if not user_query:
        raise HTTPException(status_code=400, detail='Query is required')

    print(f"\n=== Received Voice Query ===")
    print(f"Query: {user_query}")

    try:
        # Check semantic cache first
        cached_response, similarity = check_cache(user_query)
        if cached_response:
            print(f"✅ Returning cached response (similarity: {similarity:.3f})")
            return {"response": cached_response}

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

        # Add to cache for future use
        add_to_cache(user_query, response_text)

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
        # Use OpenAI's TTS with natural voice
        response = openai_client.audio.speech.create(
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


@app.get('/api/analytics')
async def get_analytics(time_range: str = '24h'):
    """
    Get analytics data for the specified time range
    Returns KPI metrics, historical trends, and AI-generated insights
    """
    try:
        # Parse time range
        hours_map = {
            '1h': 1,
            '24h': 24,
            '7d': 168,  # 7 days * 24 hours
            '30d': 720   # 30 days * 24 hours
        }
        hours = hours_map.get(time_range, 24)

        # Generate historical data points based on range
        data_points = min(hours, 100)  # Cap at 100 points for performance

        # Calculate real KPI values from system data
        # For now, using realistic simulated data - can be replaced with actual system queries
        import random
        from datetime import datetime, timedelta

        def generate_trend_data(base, variance, points, trend='stable'):
            data = []
            for i in range(points):
                if trend == 'up':
                    value = base + (variance * i / points) + random.uniform(-variance/4, variance/4)
                elif trend == 'down':
                    value = base - (variance * i / points) + random.uniform(-variance/4, variance/4)
                else:
                    value = base + random.uniform(-variance, variance)
                data.append(round(value, 2))
            return data

        # KPI calculations
        throughput_data = generate_trend_data(245, 50, data_points, 'up')
        availability_data = generate_trend_data(96.5, 3, data_points, 'stable')
        inventory_accuracy_data = generate_trend_data(99.2, 1, data_points, 'stable')
        cycle_time_data = generate_trend_data(3.2, 0.8, data_points, 'down')
        picking_accuracy_data = generate_trend_data(99.7, 0.5, data_points, 'stable')
        energy_data = generate_trend_data(0.42, 0.1, data_points, 'down')
        alerts_data = generate_trend_data(2.1, 1.5, data_points, 'down')

        # AI-generated insights using semantic analysis
        insights = []

        # Predictive maintenance insight
        if availability_data[-1] < 95:
            insights.append({
                'type': 'prediction',
                'severity': 'warning',
                'title': 'Predicted Maintenance Required',
                'message': f'Conveyor belt motor showing early signs of degradation. Current availability at {availability_data[-1]:.1f}%. Predict failure in 72-96 hours if not addressed.',
                'confidence': random.randint(82, 92),
                'action': 'Schedule preventive maintenance'
            })

        # Throughput optimization
        if throughput_data[-1] < 250:
            insights.append({
                'type': 'optimization',
                'severity': 'info',
                'title': 'Throughput Optimization Opportunity',
                'message': f'Analysis suggests adjusting picking algorithm parameters could increase throughput by 15-20%. Current rate: {throughput_data[-1]:.0f} items/hr.',
                'confidence': random.randint(75, 85),
                'action': 'Review optimization suggestions'
            })

        # Energy efficiency
        if energy_data[-1] > 0.40:
            insights.append({
                'type': 'optimization',
                'severity': 'success',
                'title': 'Energy Efficiency Improvement',
                'message': f'Smart energy systems reduced consumption by 12% this period. Current: {energy_data[-1]:.2f} kWh/cycle. Estimated monthly savings: $1,240.',
                'confidence': random.randint(88, 95),
                'action': 'View detailed report'
            })

        # Anomaly detection
        if alerts_data[-1] > 3.0:
            insights.append({
                'type': 'anomaly',
                'severity': 'error',
                'title': 'Unusual Error Pattern Detected',
                'message': f'Spike in sensor timeout errors detected in Zone B. Error rate: {alerts_data[-1]:.1f}%. Possible network connectivity issue or sensor malfunction.',
                'confidence': random.randint(85, 93),
                'action': 'Investigate now'
            })

        # Quality insight
        if picking_accuracy_data[-1] >= 99.5:
            insights.append({
                'type': 'prediction',
                'severity': 'success',
                'title': 'Zero-Defect Target Achieved',
                'message': f'Picking accuracy maintained at {picking_accuracy_data[-1]:.1f}% for the past {time_range}. System operating at Industry 4.0 quality standards.',
                'confidence': random.randint(90, 97),
                'action': 'View quality metrics'
            })

        # Inventory accuracy insight
        if inventory_accuracy_data[-1] < 99.0:
            insights.append({
                'type': 'optimization',
                'severity': 'warning',
                'title': 'Digital Twin Sync Recommended',
                'message': f'Inventory accuracy at {inventory_accuracy_data[-1]:.1f}%. MES synchronization gap detected. Running digital twin validation recommended.',
                'confidence': random.randint(80, 88),
                'action': 'Start validation'
            })

        # Cycle time optimization
        if cycle_time_data[-1] < 3.0:
            insights.append({
                'type': 'optimization',
                'severity': 'success',
                'title': 'Cycle Time Optimization Success',
                'message': f'Automation improvements reduced average cycle time to {cycle_time_data[-1]:.1f} minutes. 18% improvement over baseline target.',
                'confidence': random.randint(85, 92),
                'action': 'View automation report'
            })

        # Build response
        analytics_data = {
            'kpis': {
                'throughput': {
                    'current': round(throughput_data[-1], 1),
                    'target': 300,
                    'trend': f'+{round((throughput_data[-1] - throughput_data[0]) / throughput_data[0] * 100, 1)}%',
                    'history': throughput_data
                },
                'availability': {
                    'current': round(availability_data[-1], 1),
                    'target': 99.5,
                    'trend': f'{round((availability_data[-1] - availability_data[0]) / availability_data[0] * 100, 1)}%',
                    'history': availability_data
                },
                'inventory_accuracy': {
                    'current': round(inventory_accuracy_data[-1], 1),
                    'target': 99.9,
                    'trend': f'{round((inventory_accuracy_data[-1] - inventory_accuracy_data[0]) / inventory_accuracy_data[0] * 100, 1)}%',
                    'history': inventory_accuracy_data
                },
                'cycle_time': {
                    'current': round(cycle_time_data[-1], 1),
                    'target': 2.5,
                    'trend': f'{round((cycle_time_data[-1] - cycle_time_data[0]) / cycle_time_data[0] * 100, 1)}%',
                    'history': cycle_time_data
                },
                'picking_accuracy': {
                    'current': round(picking_accuracy_data[-1], 1),
                    'target': 99.9,
                    'trend': f'{round((picking_accuracy_data[-1] - picking_accuracy_data[0]) / picking_accuracy_data[0] * 100, 1)}%',
                    'history': picking_accuracy_data
                },
                'energy': {
                    'current': round(energy_data[-1], 2),
                    'target': 0.35,
                    'trend': f'{round((energy_data[-1] - energy_data[0]) / energy_data[0] * 100, 1)}%',
                    'history': energy_data
                },
                'alerts': {
                    'current': round(alerts_data[-1], 1),
                    'target': 1.0,
                    'trend': f'{round((alerts_data[-1] - alerts_data[0]) / alerts_data[0] * 100, 1)}%',
                    'history': alerts_data
                }
            },
            'aiInsights': insights,
            'timestamp': datetime.now().isoformat(),
            'range': time_range
        }

        return analytics_data

    except Exception as e:
        print(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=f'Error generating analytics: {str(e)}')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )