history_store = {}

def add_history(user_id, message, sender):
    if user_id not in history_store:
        history_store[user_id] = []
    history_store[user_id].append({
        "sender": sender,
        "message": message
    })

def get_history(user_id):
    return history_store.get(user_id, [])

def clear_history(user_id):
    history_store[user_id] = []