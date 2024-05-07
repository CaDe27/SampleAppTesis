from app import create_app
import argparse

app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask application on.')
    args = parser.parse_args()
    app.run(debug=True, port=args.port)