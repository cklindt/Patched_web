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
        if not request.is_json:
            return jsonify({'error': 'JSON payload required'}), 400
            
        req = request.json.get('command', '')

        if not req or not isinstance(req, str):
            return jsonify({'error': 'Invalid command provided'}), 400
        
        if req in ALLOWED_API_COMMANDS:
            cmd_args = ALLOWED_API_COMMANDS[req]
            # Additional validation to ensure no command injection
            for arg in cmd_args:
                if not isinstance(arg, str) or ';' in arg or '|' in arg or '&' in arg or '>' in arg or '<' in arg:
                    return jsonify({'error': 'Invalid command structure'}), 403
                    
            result = subprocess.run(cmd_args, capture_output=True, text=True, shell=False)
            return jsonify({'status': result.stdout.strip().splitlines()}), 200
        else:
            return jsonify({'error': 'Command not allowed'}), 403
    
    except Exception as e:
        # Log the error but don't expose it to the user
        return jsonify({'error': 'An error occurred'}), 500