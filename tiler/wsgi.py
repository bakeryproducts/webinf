from server import app

if __name__ == "__main__":
    host, port = '0.0.0.0', 5000
    app.run(host=host, port=port)
