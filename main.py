import config
from app import create_app

app = create_app()


@app.context_processor
def inject_config():
    return dict(config=config)


if __name__ == "__main__":
    app.run(debug=False, port=config.web_app_port, host=config.web_app_host)
