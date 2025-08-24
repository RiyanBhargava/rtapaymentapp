from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import qrcode
import base64
from io import BytesIO
import re
from byteplussdkarkruntime import Ark
import config
import os

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Initialize Ark client
client = Ark(
    base_url=config.BYTEPLUS_BASE_URL,
    api_key=config.BYTEPLUS_API_KEY
)

def load_sample_journey():
    """Load sample journey from JSON file"""
    try:
        with open('sample_journey.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['sample_journey']
    except Exception as e:
        print(f"Error loading sample journey: {e}")
        # Fallback sample if file can't be loaded
        return {
            "title": "Sample Journey",
            "description": "Default multi-modal journey",
            "journey_text": "1. taxi: 1 stop, 8.5 min, 4.2 km\n   Stops: Dubai Marina Walk -> Mall of the Emirates Metro Station\n\n2. MRed1 (metro): 7 stops, 12.1 min, 15.8 km\n   Stops: Mall of the Emirates Metro Station 1 -> Union Metro Station 2\n\n3. 64 (bus): 8 stops, 18.3 min, 12.4 km\n   Stops: Union Bus Terminal -> Gold Souq Bus Station"
        }

def save_calculated_fares_to_json(journey_info):
    """Save BytePlus AI-calculated fares back to the JSON file"""
    try:
        # Load current JSON data
        with open('sample_journey.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create calculated_fares section with AI results
        calculated_fares = {
            "total": journey_info.get('total_fare', 0),
            "breakdown": {},
            "calculated_by": "BytePlus AI",
            "timestamp": "live_calculation"
        }
        
        # Add individual transport mode fares
        for step in journey_info.get('journey_steps', []):
            mode = step.get('mode', 'unknown')
            if mode not in ['walk', 'transfer']:  # Skip walking transfers
                fare = step.get('fare_aed', 0)
                if mode in calculated_fares["breakdown"]:
                    calculated_fares["breakdown"][mode] += fare
                else:
                    calculated_fares["breakdown"][mode] = fare
        
        # Update the JSON with calculated fares
        data['sample_journey']['calculated_fares'] = calculated_fares
        
        # Save back to file
        with open('sample_journey.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Updated JSON with AI-calculated fares: Total {calculated_fares['total']} AED")
        
    except Exception as e:
        print(f"Error saving calculated fares: {e}")

# Fare rates (in AED) - moved to config.py
FARE_RATES = {
    'taxi': config.TAXI_PER_KM,
    'metro': config.METRO_PER_KM,
    'bus': config.BUS_PER_KM,
    'transfer': 0.0  # walking transfers are free
}

# Dubai transport stops - from config
STOPS_LIST = ', '.join(config.DUBAI_STOPS)

def parse_journey_text(journey_text):
    """Parse the journey text and extract transport modes, distances, and stops"""
    lines = journey_text.strip().split('\n')
    journey_steps = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and headers
        if not line or line.startswith('===') or line.startswith('---'):
            i += 1
            continue
            
        # Look for numbered steps with transport info
        if '. ' in line and ('km' in line or 'min' in line):
            # Extract step number and details
            try:
                # Parse the line to get mode and details
                parts = line.split(': ', 1)
                if len(parts) >= 2:
                    # Extract mode from the first part
                    step_part = parts[0].strip()
                    details = parts[1].strip()
                    
                    # Extract transport mode - handle different formats
                    mode = None
                    line_number = None
                    
                    # Check for patterns like "1. taxi:" or "3. MRed1 (metro):" or "5. 64 (bus):"
                    if 'taxi' in step_part.lower():
                        mode = 'taxi'
                    elif '(metro)' in step_part.lower():
                        mode = 'metro'
                        # Extract line number like "MRed1"
                        mode_match = re.search(r'(\w+)\s*\(metro\)', step_part)
                        if mode_match:
                            line_number = mode_match.group(1)
                    elif '(bus)' in step_part.lower():
                        mode = 'bus'
                        # Extract route number like "64"
                        mode_match = re.search(r'(\d+)\s*\(bus\)', step_part)
                        if mode_match:
                            line_number = mode_match.group(1)
                    elif 'transfer' in step_part.lower() or 'walk' in step_part.lower():
                        mode = 'transfer'
                    
                    if mode:
                        # Extract distance
                        distance_match = re.search(r'(\d+\.?\d*)\s*km', details)
                        distance = float(distance_match.group(1)) if distance_match else 0
                        
                        # Look for stops in next line
                        stops = []
                        if i + 1 < len(lines) and lines[i + 1].strip().startswith('Stops:'):
                            stops_line = lines[i + 1].strip()
                            stops_text = stops_line.replace('Stops:', '').strip()
                            stops = [stop.strip() for stop in stops_text.split('->')]
                            i += 1  # Skip the stops line
                        
                        journey_steps.append({
                            'mode': mode,
                            'line_number': line_number,
                            'distance': distance,
                            'stops': stops,
                            'completed': False
                        })
                        
            except Exception as e:
                print(f"Error parsing line '{line}': {e}")
                
        i += 1
    
    return journey_steps

def calculate_fare(mode, distance, line_number=None):
    """Calculate fare based on transport mode and distance"""
    if mode == 'taxi':
        fare = max(config.TAXI_BASE_FARE, config.TAXI_PER_KM * distance)  # Minimum base fare
    elif mode == 'metro':
        fare = config.METRO_BASE_FARE + (distance * config.METRO_PER_KM)
    elif mode == 'bus':
        fare = config.BUS_BASE_FARE + (distance * config.BUS_PER_KM)
    else:
        fare = 0.0
    
    # Round to whole numbers for clean display
    return round(fare)

def generate_qr_code(data):
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def get_journey_info_from_ai(journey_text):
    """Use ByteDance AI to extract and structure journey information"""
    try:
        response = client.chat.completions.create(
            model=config.BYTEPLUS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Dubai RTA transport assistant. Extract transport information from journey descriptions and return structured data."
                },
                {
                    "role": "user",
                    "content": f"""
Journey text: {journey_text}

Please extract the following information and return as JSON:
{{
    "journey_steps": [
        {{
            "step_number": 1,
            "mode": "taxi|metro|bus|transfer|walk",
            "line_number": "route number if applicable",
            "distance_km": "distance in km as float",
            "duration_min": "duration in minutes as float", 
            "stops": ["start_stop", "end_stop"],
            "fare_aed": "calculated fare in AED"
        }}
    ],
    "total_fare": "total fare for entire journey",
    "total_distance": "total distance in km",
    "total_duration": "total duration in minutes"
}}

Use Dubai RTA fare structure: Taxi minimum {config.TAXI_BASE_FARE} AED + {config.TAXI_PER_KM} AED/km, Metro {config.METRO_BASE_FARE}-{config.METRO_BASE_FARE + 5} AED, Bus {config.BUS_BASE_FARE}-{config.BUS_BASE_FARE + 3} AED, Walking transfers free.
"""
                }
            ],
        )
        
        ai_response = response.choices[0].message.content
        # Try to parse JSON from AI response
        try:
            ai_data = json.loads(ai_response)
            # Round all fare values in AI response
            if 'journey_steps' in ai_data:
                for step in ai_data['journey_steps']:
                    if 'fare_aed' in step:
                        step['fare_aed'] = round(float(step['fare_aed']))
            if 'total_fare' in ai_data:
                ai_data['total_fare'] = round(float(ai_data['total_fare']))
            return ai_data
        except:
            # Fallback to manual parsing if AI doesn't return valid JSON
            return parse_journey_manually(journey_text)
            
    except Exception as e:
        print(f"AI processing error: {e}")
        return parse_journey_manually(journey_text)

def parse_journey_manually(journey_text):
    """Fallback manual parsing"""
    steps = parse_journey_text(journey_text)
    total_fare = 0
    
    journey_steps = []
    for i, step in enumerate(steps):
        fare = calculate_fare(step['mode'], step['distance'], step.get('line_number'))
        total_fare += fare
        
        journey_steps.append({
            "step_number": i + 1,
            "mode": step['mode'],
            "line_number": step.get('line_number'),
            "distance_km": step['distance'],
            "stops": step['stops'],
            "fare_aed": fare,  # Already rounded in calculate_fare function
            "completed": False
        })
    
    return {
        "journey_steps": journey_steps,
        "total_fare": round(total_fare),  # Round total fare too
        "total_distance": sum(step['distance'] for step in steps),
        "journey_id": str(uuid.uuid4())
    }

@app.route('/')
def home():
    # Load sample journey data
    sample_journey = load_sample_journey()
    return render_template('index.html', sample_journey=sample_journey)

@app.route('/process_journey', methods=['POST'])
def process_journey():
    # Use the sample journey from JSON file instead of user input
    sample_journey = load_sample_journey()
    journey_text = sample_journey['journey_text']
    
    if not journey_text:
        return jsonify({'error': 'No journey data available'}), 400
    
    # Process journey using AI
    journey_info = get_journey_info_from_ai(journey_text)
    journey_info['title'] = sample_journey.get('title', 'Multi-Modal Journey')
    journey_info['description'] = sample_journey.get('description', '')
    
    # Save the AI-calculated fares back to the JSON file
    save_calculated_fares_to_json(journey_info)
    
    # Store in session
    session['journey_info'] = journey_info
    session['current_step'] = 0
    session['journey_id'] = journey_info.get('journey_id', str(uuid.uuid4()))
    session['payment_completed'] = False
    
    return jsonify(journey_info)

@app.route('/payment')
def payment_page():
    if 'journey_info' not in session:
        return redirect(url_for('home'))
    
    journey_info = session['journey_info']
    return render_template('payment.html', journey_info=journey_info)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'journey_info' not in session:
        return jsonify({'error': 'No active journey'}), 400
    
    payment_data = request.json
    payment_method = payment_data.get('payment_method')
    amount = payment_data.get('amount')
    
    # Simulate payment processing (in real app, integrate with payment gateway)
    if payment_method and amount:
        # Mark payment as completed
        session['payment_completed'] = True
        session['payment_method'] = payment_method
        session['payment_amount'] = amount
        
        return jsonify({
            'success': True,
            'transaction_id': str(uuid.uuid4()),
            'message': 'Payment processed successfully'
        })
    else:
        return jsonify({'error': 'Invalid payment data'}), 400

@app.route('/generate_qr')
def generate_qr():
    if 'journey_info' not in session or not session.get('payment_completed', False):
        return redirect(url_for('home'))
    
    journey_info = session['journey_info']
    current_step = session.get('current_step', 0)
    
    # Skip walking transfers automatically
    while (current_step < len(journey_info['journey_steps']) and 
           journey_info['journey_steps'][current_step]['mode'] in ['transfer', 'walk']):
        current_step += 1
        session['current_step'] = current_step
    
    if current_step >= len(journey_info['journey_steps']):
        # Calculate actual transport modes used (excluding walking/transfers)
        actual_transport_modes = []
        total_fare = 0
        
        for step in journey_info['journey_steps']:
            if step['mode'] not in ['transfer', 'walk']:
                fare = step.get('fare_aed', 0)
                total_fare += fare
                actual_transport_modes.append({
                    'mode': step['mode'],
                    'line_number': step.get('line_number', ''),
                    'fare': fare
                })
        
        return render_template('journey_complete.html', 
                             journey_info=journey_info,
                             actual_transport_modes=actual_transport_modes,
                             total_fare=total_fare)
    
    current_transport = journey_info['journey_steps'][current_step]
    
    # Generate QR code data for scanning purposes only (no payment)
    qr_data = {
        'journey_id': session['journey_id'],
        'step': current_step,
        'mode': current_transport['mode'],
        'action': 'scan',  # Changed from payment action to scan action
        'line_number': current_transport.get('line_number'),
        'purpose': 'entry' if current_transport['mode'] in ['metro', 'bus'] else 'exit'
    }
    
    qr_code_img = generate_qr_code(json.dumps(qr_data))
    
    return render_template('qr_code.html', 
                         qr_code=qr_code_img, 
                         transport_info=current_transport,
                         current_step=current_step + 1,
                         total_steps=len([s for s in journey_info['journey_steps'] if s['mode'] not in ['transfer', 'walk']]),
                         payment_completed=True)

@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    qr_data = request.json.get('qr_data', '')
    
    try:
        scan_info = json.loads(qr_data)
        journey_id = scan_info.get('journey_id')
        
        if journey_id != session.get('journey_id'):
            return jsonify({'error': 'Invalid QR code'}), 400
        
        current_step = session.get('current_step', 0)
        journey_info = session['journey_info']
        
        # Handle different scan actions
        action = scan_info.get('action', 'scan')
        mode = scan_info.get('mode')
        
        if action == 'scan':
            if mode == 'taxi':
                # Taxi - single scan to exit
                session['current_step'] = current_step + 1
                return jsonify({
                    'success': True, 
                    'action': 'exit_taxi',
                    'show_animation': True,
                    'animation_duration': 8000,  # 8 seconds
                    'message': 'Taxi journey completed!',
                    'next_step': True
                })
            elif mode in ['metro', 'bus']:
                purpose = scan_info.get('purpose', 'entry')
                if purpose == 'entry':
                    # Metro/Bus entry scan
                    return jsonify({
                        'success': True, 
                        'action': f'enter_{mode}',
                        'show_animation': True,
                        'animation_duration': 8000,  # 8 seconds
                        'message': f'Entered {mode}!',
                        'need_exit_qr': True
                    })
                elif purpose == 'exit':
                    # Metro/Bus exit scan
                    session['current_step'] = current_step + 1
                    return jsonify({
                        'success': True, 
                        'action': f'exit_{mode}',
                        'show_animation': True,
                        'animation_duration': 8000,  # 8 seconds
                        'message': f'Exited {mode}!',
                        'next_step': True
                    })
                    
    except Exception as e:
        return jsonify({'error': 'Invalid QR code format'}), 400

@app.route('/generate_exit_qr')
def generate_exit_qr():
    if 'journey_info' not in session or not session.get('payment_completed', False):
        return redirect(url_for('home'))
    
    journey_info = session['journey_info']
    current_step = session.get('current_step', 0)
    current_transport = journey_info['journey_steps'][current_step]
    
    # Generate exit QR code for metro/bus
    qr_data = {
        'journey_id': session['journey_id'],
        'step': current_step,
        'mode': current_transport['mode'],
        'action': 'scan',
        'line_number': current_transport.get('line_number'),
        'purpose': 'exit'
    }
    
    qr_code_img = generate_qr_code(json.dumps(qr_data))
    
    return render_template('exit_qr.html', 
                         qr_code=qr_code_img, 
                         transport_info=current_transport,
                         current_step=current_step + 1,  # Add 1 for display (1-based indexing)
                         session=session)

@app.route('/journey_status')
def journey_status():
    if 'journey_info' not in session:
        return jsonify({'error': 'No active journey'}), 400
    
    journey_info = session['journey_info']
    current_step = session.get('current_step', 0)
    
    return jsonify({
        'current_step': current_step,
        'total_steps': len(journey_info['journey_steps']),
        'completed': current_step >= len(journey_info['journey_steps']),
        'journey_info': journey_info
    })

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
