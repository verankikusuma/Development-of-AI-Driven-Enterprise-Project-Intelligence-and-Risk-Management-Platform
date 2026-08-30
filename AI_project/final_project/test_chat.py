from utils.app_store import create_user, authenticate, create_conversation, add_message, list_messages, init_db

init_db()

try:
    user = create_user("testuser_chat", "password123", "Full Stack Developer")
    user_id = user["id"]
except:
    auth = authenticate("testuser_chat", "password123")
    user_id = auth["id"]

conv = create_conversation(user_id, "Test Title")
conv_id = conv["id"]

print("Conversation created:", conv_id)

add_message(user_id, conv_id, "user", "Hello this is a test")
msgs = list_messages(user_id, conv_id)
print("Messages after user add:", [m["content"] for m in msgs])

add_message(user_id, conv_id, "assistant", "Hello back", ["doc1.pdf"])
msgs = list_messages(user_id, conv_id)
print("Messages after assistant add:", [(m["role"], m["content"]) for m in msgs])

