from datetime import datetime


def message_serializer(a) -> dict:
    return{
        "author": a.author,
        "message": a.message,
        "timestamp": (a.timestamp).strftime("%a. %I:%M %p"),
        "short_id": a.short_id
    }

# def message_serializer(a) -> dict:
#     return{
#         "author": a["username"],
#         "message": a["message"],
#         "timestamp": datetime.now().strftime("%a. %I:%M %p")
#     }