from app import app, dispatcher
from app.utils import get_update_from_request


@app.route('/', methods=['GET'])
def index():
    return 'OK'


@app.route('/bot', methods=['GET', 'POST'])
def bot_handler():
    update = get_update_from_request()
    dispatcher.process_update(update)
    return 'OK'
