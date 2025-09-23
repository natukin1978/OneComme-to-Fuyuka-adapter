import logging
import random
from random import randint
from typing import Any, Dict

logger = logging.getLogger(__name__)


def is_hit(percent: int) -> bool:
    if percent >= 100:
        return True
    random_value = randint(0, 100)
    result = percent >= random_value
    if result:
        logger.info("hit!")
    else:
        logger.info("skip.")
    logger.info(f"{percent}% の確率で、{random_value}% の位置でした。")
    return result


def is_hit_by_message_json(percent: int, json_data: Dict[str, Any]) -> bool:
    if json_data["isFirst"] or json_data["isFirstOnStream"]:
        # 初見さんや配信で初回の人への回答は必須
        percent = 100
    return is_hit(percent)
