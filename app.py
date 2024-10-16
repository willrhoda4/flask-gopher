




import os
from   flask  import Flask
from   dotenv import load_dotenv
import cloudinary

# Importing handlers
from handlers.flicks_handler  import get_flicks
from handlers.posters_handler import fetch_and_upload_poster
from handlers.update_database import update_database
from scripts.stealth_test     import stealth_test

# Load environment variables from .env file
load_dotenv()
print(os.getenv("CLOUD_NAME"))

# Initialize Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

app = Flask(__name__)


@app.route("/hello", methods=["GET"])
def hello_world():
    return "Hello, World!"


@app.route("/getFlicks", methods=["POST"])
def flicks():
    return get_flicks()


@app.route("/getPoster", methods=["POST"])
def poster():
    return fetch_and_upload_poster()

@app.route('/updateDb', methods=['GET'])
def update():
    return update_database()

@app.route('/stealthTest', methods=['GET'])
def stealth():
    return stealth_test()



if __name__ == "__main__":
    app.run(debug=True)
