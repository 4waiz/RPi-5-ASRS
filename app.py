import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['OMP_NUM_THREADS'] = '1'

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import openai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random

# --- API key setup ---
openai.api_key = OPENAI_API_KEY
if not openai.api_key:
    print("=" * 80)
    print("ERROR: OPENAI_API_KEY not set!")
    print("=" * 80)
# ----------------------

MODEL_NAME = 'all-MiniLM-L6-v2'
EXCEL_PATH = 'data/machine_errors.xlsx'

# ... (the rest of your file remains unchanged)

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
        df = pd.read_excel(EXCEL_PATH).fillna('')
        print(f"✓ Loaded {len(df)} rows from Excel")
    except FileNotFoundError:
        print(f"ERROR: The data file was not found at '{EXCEL_PATH}'.")
        print(f"Please ensure the file exists at: {os.path.abspath(EXCEL_PATH)}")
        print("Creating sample alerts without Excel data...")
        alerts_data = generate_sample_alerts()
        return
    except Exception as e:
        print(f"ERROR loading Excel: {e}")
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
    sample_size = min(25, len(df))
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
    if not openai.api_key:
        return "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."

    system_prompt = """
    You are an expert ASRS (Automated Storage and Retrieval System) maintenance assistant.
    Your role is to help a technician diagnose and resolve a machine error.
    Use the provided 'Context from Past Incidents' to give a clear, structured, and actionable response.
    If the context is not relevant, rely on your general knowledge of industrial automation and robotics.

    Structure your response in three parts:
    1.  **Potential Issue:** Briefly describe what the problem might be based on the query and context.
    2.  **Recommended Actions:** Provide a numbered list of concrete steps the technician should take. Start with the simplest and safest checks.
    3.  **Preventative Measures:** Suggest what can be done to prevent this issue in the future, based on the context.

    Always be clear, concise, and professional.
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
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt}
            ],
            temperature=0.5,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Sorry, I encountered an error while generating a response: {str(e)}"


def get_diagnostic_options():
    global df
    if df is None:
        return []

    subsystems = df['subsystem'].unique().tolist()
    return subsystems


app = Flask(__name__)
CORS(app)

with app.app_context():
    initialize_rag()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/initial-data', methods=['GET'])
def get_initial_data():
    diagnostic_options = get_diagnostic_options()

    # Add severity levels info for frontend
    severity_info = {
        'levels': SEVERITY_LEVELS,
        'description': 'FMEA-based alert classification with RPN (Risk Priority Number)'
    }

    print(f"\n=== API: Sending {len(alerts_data)} alerts to frontend ===")

    return jsonify({
        "diagnosticOptions": diagnostic_options,
        "alerts": alerts_data,
        "severityInfo": severity_info
    })


@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Invalid request. "query" is required.'}), 400

    user_query = data['query']

    print(f"\n=== Received Voice Query ===")
    print(f"Query: {user_query}")

    try:
        context = retrieve_context(user_query)
        response_text = generate_response(user_query, context)

        print(f"Response generated successfully")

        return jsonify({'response': response_text})
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    filter_type = request.args.get('filter', 'all')

    print(f"\n=== API: Filtering alerts by '{filter_type}' ===")

    filtered_alerts = alerts_data

    if filter_type == 'critical':
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'critical']
    elif filter_type == 'error':
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'error']
    elif filter_type == 'warning':
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'warning']
    elif filter_type == 'alerts':
        # Legacy support: show critical + error
        filtered_alerts = [a for a in alerts_data if a['severity'] in ['critical', 'error']]
    elif filter_type == 'warnings':
        # Legacy support
        filtered_alerts = [a for a in alerts_data if a['severity'] == 'warning']

    print(f"Returning {len(filtered_alerts)} alerts")

    return jsonify({'alerts': filtered_alerts})


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Starting Flask Backend Server")
    print("="*80)
    print(f"Server will run on: http://localhost:5001")
    print(f"API Endpoints:")
    print(f"  - GET  /api/initial-data")
    print(f"  - POST /api/query")
    print(f"  - GET  /api/alerts")
    print("="*80 + "\n")

    app.run(debug=True, port=5001)
