contexts = {}

def save_context(scope, context_id, version, payload):
    key = f"{scope}:{context_id}"
    existing = contexts.get(key)
    if existing and existing["version"] >= version:
        return False
    contexts[key] = {"version": version, "payload": payload}
    return True

def get_context(scope, context_id):
    key = f"{scope}:{context_id}"
    return contexts.get(key, {}).get("payload", {})