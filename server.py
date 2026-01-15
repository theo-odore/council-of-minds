from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import uuid
import logging

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# Configuration
OLLAMA_API = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:latest"

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Stores
PHILOSOPHERS = {
    'socrates': {
        'name': 'Socrates',
        'model': 'mistral',
        'prompt': "You are Socrates. Challenge the last speaker with a probing question. Do not preach. Keep it very concise (max 25 words)."
    },
    'kafka': {
        'name': 'Franz Kafka',
        'model': 'qwen',
        'prompt': "You are Kafka. Murmur a pessimistic observation. Be weird. Keep it very concise (max 25 words)."
    },
    'dostoevsky': {
        'name': 'Fyodor Dostoevsky',
        'model': 'phi',
        'prompt': "You are Dostoevsky. Make an intense emotional outburst. Be dramatic. Keep it very concise (max 25 words)."
    },
    'nietzsche': {
        'name': 'Friedrich Nietzsche',
        'model': 'llama3.2',
        'prompt': "You are Nietzsche. Mock the previous speaker. Be arrogant. Keep it very concise (max 25 words)."
    },
    'chekhov': {
        'name': 'Anton Chekhov',
        'model': 'gemma',
        'prompt': "You are Chekhov. Make a dry, clinical observation. Point out the irony. Keep it very concise (max 25 words)."
    }
}

# Sessions: { session_id: { id, title, history: [] } }
SESSIONS = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/philosophers', methods=['GET'])
def get_philosophers():
    return jsonify(PHILOSOPHERS)

@app.route('/philosophers/<pid>/model', methods=['PUT'])
def update_philosopher_model(pid):
    if pid not in PHILOSOPHERS:
        return jsonify({"error": "Philosopher not found"}), 404
    
    data = request.json
    new_model = data.get('model')
    if not new_model:
        return jsonify({"error": "Model name required"}), 400
    
    PHILOSOPHERS[pid]['model'] = new_model
    logger.info(f"Updated {pid} model to {new_model}")
    return jsonify({"success": True, "model": new_model})

@app.route('/sessions', methods=['GET'])
def get_sessions():
    # Return list of sessions summary
    return jsonify([{"id": s['id'], "title": s['title']} for s in SESSIONS.values()])

@app.route('/sessions', methods=['POST'])
def create_session():
    sid = str(uuid.uuid4())[:8]
    session = {
        "id": sid,
        "title": f"Session {sid}",
        "history": [],
        "last_speaker": None
    }
    SESSIONS[sid] = session
    return jsonify(session)

@app.route('/sessions/<sid>', methods=['GET'])
def get_session(sid):
    if sid not in SESSIONS:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(SESSIONS[sid])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    sid = data.get('session_id')
    user_input = data.get('input') # If None, it's a philosopher turn
    
    if sid not in SESSIONS:
        return jsonify({"error": "Session not found"}), 404
    
    session = SESSIONS[sid]
    
    # 1. Handle Human Input (Chairman)
    if user_input:
        session['history'].append({"speaker": "Chairman", "text": user_input})
        session['last_speaker'] = "Chairman"
        # Update title if it's the first message
        if len(session['history']) == 1:
            session['title'] = user_input[:30] + "..."
        return jsonify({"status": "received"})

    # 2. Handle Philosopher Turn
    # Strategy: Strict Round-Robin. Everyone must speak once before anyone repeats.
    
    # Identify speakers since the last Chairman input
    speakers_since_chairman = set()
    for m in reversed(session['history']):
        if m['speaker'] == 'Chairman':
            break
        speakers_since_chairman.add(m['speaker'])
            
    # Who hasn't spoken yet?
    all_names = {p['name'] for p in PHILOSOPHERS.values()}
    remaining_names = all_names - speakers_since_chairman
    
    if remaining_names:
        # Pick from those who haven't spoken
        available = [pid for pid, data in PHILOSOPHERS.items() if data['name'] in remaining_names]
    else:
        # Everyone has spoken. Start new cycle (but avoid immediate repeat)
        available = [pid for pid in PHILOSOPHERS.keys() if PHILOSOPHERS[pid]['name'] != session['last_speaker']]

    import random
    speaker_id = random.choice(available)
    speaker = PHILOSOPHERS[speaker_id]
    
    # Build Context (Last few messages)
    context_msgs = session['history'][-5:]
    context_str = "\n".join([f"{m['speaker']}: {m['text']}" for m in context_msgs])
    last_speaker_name = session['last_speaker'] or "Chairman"

    # Find the main topic (last Chairman message)
    chairman_topic = "Existence"
    for m in reversed(session['history']):
        if m['speaker'] == 'Chairman':
            chairman_topic = m['text']
            break

    full_prompt = f"""
    Context of the conversation:
    {context_str}
    
    Current Topic (Proposed by Chairman): "{chairman_topic}"
    
    Your role:
    {speaker['prompt']}
    
    Instruction:
    The last person to speak was {last_speaker_name}. Start by addressing them by name (e.g., "But {last_speaker_name}, ...").
    You must argue with their point, BUT you must also relate it back to the Chairman's topic: "{chairman_topic}".
    Don't just bicker; use your philosophy to answer the Chairman's question through your rebuttal.
    Be extremely brief (max 2 sentences).
    """
    
    target_model = speaker.get('model', DEFAULT_MODEL)
    
    try:
        logger.info(f"Asking {speaker['name']} using model {target_model}...")
        r = requests.post(OLLAMA_API, json={
            "model": target_model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": 40, # strict token limit (approx 30 words)
                "temperature": 0.8
            }
        })
        r.raise_for_status()
        response_text = r.json().get('response', '').strip()
        
        # Save
        session['history'].append({"speaker": speaker['name'], "text": response_text})
        session['last_speaker'] = speaker['name']
        
        return jsonify({
            "speaker": speaker['name'],
            "speaker_id": speaker_id,
            "text": response_text
        })
        
    except Exception as e:
        logger.error(f"Ollama Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Council Server running on http://localhost:5000")
    app.run(port=5000, debug=True)
