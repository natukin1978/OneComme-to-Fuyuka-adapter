import datetime

from one_comme_users import OneCommeUsers


def create_message_json(data: dict[str, any]) -> dict[str, any]:
    localtime = datetime.datetime.now()
    localtime_iso_8601 = localtime.isoformat()
    json_data = {
        "dateTime": localtime_iso_8601,
        "id": data["userId"],
        "displayName": data["displayName"],
        "nickname": None,  # すぐ下で設定する
        "content": data["comment"],
        "isFirst": False,
        "isFirstOnStream": None,  # すぐ下で設定する
        "noisy": False,
        "additionalRequests": None,  # すぐ下で設定する
    }
    OneCommeUsers.update_message_json(json_data)
    return json_data
