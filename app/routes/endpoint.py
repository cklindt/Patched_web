from flask import Blueprint, request, jsonify
import subprocess

endpoint_bp = Blueprint("endpoint", __name__)

@endpoint_bp.route("/endpoint", methods=['POST'])
def endpoint():
    ALLOWED_API_COMMANDS = {
            'system_info':['uname','-a'],
            'disk_usage':['df','-h'],
            'memory_usage':['free','-h']
            }
    try:
        req = request.json.get('command', '')

        if not req:
            return jsonify({'error': 'No command provided'}), 400
        
        if req in ALLOWED_API_COMMANDS:
            result = subprocess.run(ALLOWED_API_COMMANDS[req], capture_output=True, text=True, shell=False)
            return jsonify({'status': result.stdout.strip().splitlines()}), 200
        else:
            return jsonify({'error': 'Command not allowed'}), 403
    
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500  # Don't expose detailed error