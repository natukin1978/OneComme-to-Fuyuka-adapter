import json

import global_value as g


class Fuyuka:

    @staticmethod
    async def send_message_by_json(json_data: dict[str, any]) -> None:
        if not g.websocket_fuyuka:
            return
        json_str = json.dumps(json_data)
        await g.websocket_fuyuka.send(json_str)

    @staticmethod
    async def send_message_by_json_with_buf(
        json_data: dict[str, any], needs_response: bool
    ) -> None:
        await Fuyuka.send_message_by_json(json_data)
