from flask import Flask, jsonify
import pandas as pd
import os
import json 
import random
from pathlib import Path


config = None
def load_config():
    current_script_path = Path(__file__).resolve()
    grandparent_directory = current_script_path.parent.parent.parent
    config_path = grandparent_directory / 'config.json'
    with open(config_path, 'r') as config_file:
        global config
        config = json.load(config_file)

def get_service_url(service_name):
    host = config['host']
    service_port = config['ports'][service_name]
    return f"http://{host}:{service_port}"


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    load_config()
    
    ad_database = [
        # Brilliant
        { 'title': 'Learn by doing',
            'text': 'Guided interactive problem solving thats effective and fun. Master concepts in 15 minutes a day.',
            'top_image_url':    f'{get_service_url("ad")}/static/images/brilliant/top.png', 
            'bottom_image_url': f'{get_service_url("ad")}/static/images/brilliant/bottom.png',
            'color': '#0080ff'
        },

        # Three Blue One Brown
        {'title': 'Animated math',
            'text': 'Latest video: But what is a GPT? Visual intro to Transformers | Deep learning, chapter 5',
            'top_image_url':    f'{get_service_url("ad")}/static/images/3b1b/top.png', 
            'bottom_image_url': f'{get_service_url("ad")}/static/images/3b1b/bottom.png',
            'color': '#000000'
        },

        # Reducible
        {'title': 'Reducing problems to their simplest form',
            'text': 'This channel is all about animating computer science concepts in a fun, interactive, and intuitive manner.',
            'top_image_url':    f'{get_service_url("ad")}/static/images/reducible/top.png', 
            'bottom_image_url': f'{get_service_url("ad")}/static/images/reducible/bottom.png',
            'color': '#9933ff'
        },

        # ITAM 
        {'title': '¿Quieres estudiar en el ITAM?',
            'text': '¡Ponte en contacto con nosotros! De lo que ya eres a lo que quieres ser.',
            'top_image_url':    f'{get_service_url("ad")}/static/images/itam/top.png', 
            'bottom_image_url': f'{get_service_url("ad")}/static/images/itam/bottom.png',
            'color' : '#006633'
        }
    ]

    @app.route('/api/ad', methods=['GET'])
    def get_ad():
        random_ad = ad_database[random.randint(0, len(ad_database)-1)]
        return jsonify(random_ad)

    return app

