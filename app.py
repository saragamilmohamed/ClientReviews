from pyngrok import ngrok, conf
from FlaskApp import app
import os



ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))

public_url = ngrok.connect(5000)
print("✅ Public ngrok URL:", public_url)

app.run(port=5000)