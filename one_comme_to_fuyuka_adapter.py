import asyncio
import json
import logging
import os
import sys

import global_value as g
from logging_setup import setup_app_logging

g.app_name = "one_comme_to_fuyuka_adapter"
g.base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# ロガーの設定
setup_app_logging(log_file_path=f"{g.app_name}.log")
logger = logging.getLogger(__name__)

from config_helper import read_config
from fuyuka_helper import Fuyuka
from one_comme_message_helper import create_message_json
from one_comme_users import OneCommeUsers
from random_helper import is_hit_by_message_json
from text_helper import read_text, read_text_set
from websocket_helper import websocket_listen_forever

print("前回の続きですか？(y/n) ", end="")
is_continue = input() == "y"

g.ADDITIONAL_REQUESTS_PROMPT = read_text("prompts/additional_requests_prompt.txt")

g.config = read_config()

g.map_is_first_on_stream = {}
g.set_exclude_id = read_text_set("exclude_id.txt")
g.websocket_stream_live = None
g.websocket_fuyuka = None


async def main():
    def get_fuyukaApi_baseUrl() -> str:
        conf_fa = g.config["fuyukaApi"]
        if not conf_fa:
            return ""
        return conf_fa["baseUrl"]

    def get_oneComme_baseUrl() -> str:
        conf_oc = g.config["oneComme"]
        if not conf_oc:
            return ""
        return conf_oc["baseUrl"]

    def set_ws_stream_live(ws) -> None:
        g.websocket_stream_live = ws

    def is_enable_service(name: str) -> bool:
        return name in g.config["stream"]["enableServices"]

    async def recv_stream_live_response(message: str) -> None:
        try:
            json_data = json.loads(message)
            if json_data["type"] != "comments":
                return

            data = json_data["data"]
            for comment in data["comments"]:
                if not is_enable_service(comment["service"]):
                    continue

                logger.info(comment)
                data = comment["data"]
                json_data = create_message_json(data)
                if json_data["id"] in g.set_exclude_id:
                    # 無視するID
                    return

                answer_level = g.config["fuyukaApi"]["answerLevel"]
                answer_length = g.config["fuyukaApi"]["answerLength"]["default"]
                needs_response = is_hit_by_message_json(answer_level, json_data)
                OneCommeUsers.update_additional_requests(json_data, answer_length)
                await Fuyuka.send_message_by_json_with_buf(json_data, needs_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error JSONDecode: {e}")
        except Exception as e:
            logger.error(f"Error : {e}")

    def set_ws_fuyuka(ws) -> None:
        g.websocket_fuyuka = ws

    async def recv_fuyuka_response(message: str) -> None:
        return

    fuyukaApi_baseUrl = get_fuyukaApi_baseUrl()
    if fuyukaApi_baseUrl:
        websocket_uri = f"{fuyukaApi_baseUrl}/chat/{g.app_name}"
        asyncio.create_task(
            websocket_listen_forever(websocket_uri, recv_fuyuka_response, set_ws_fuyuka)
        )

    oneComme_baseUrl = get_oneComme_baseUrl()
    if oneComme_baseUrl:
        websocket_uri = f"{oneComme_baseUrl}/sub?p=comments"
        asyncio.create_task(
            websocket_listen_forever(
                websocket_uri, recv_stream_live_response, set_ws_stream_live
            )
        )

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass
    finally:
        pass


if __name__ == "__main__":
    asyncio.run(main())
