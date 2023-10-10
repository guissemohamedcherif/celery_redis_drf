from backend.settings import PUSHER_CLIENT


def pusher(event, data={}):
    try:
        PUSHER_CLIENT.trigger('my-channel', event, data)
    except ValueError:
        pass
