from . import api_blueprint
from flask import request, jsonify


@api_blueprint.route('/send_message', methods=['post'])
def send_message():
    content = request.json
    message = content.get('message', '')
    response = {'message': f'Your message was received: {message}'}
    return jsonify(response), 200


@api_blueprint.route('/get_message', methods=['get'])
def get_message():
    pass


@api_blueprint.route('/upload_photo', methods=['post'])
def upload_photo():
    pass


@api_blueprint.route('/upload_audio', methods=['post'])
def upload_audio():
    pass


@api_blueprint.route('/init', methods=['get'])
def init():
    pass
