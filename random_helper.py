import logging
import random
from typing import Any, Dict

import probability_controller

logger = logging.getLogger(__name__)


def is_hit(percent: int) -> bool:
    if percent >= 100:
        return True
    probability_controller.increment_comment_count()
    response_probability = probability_controller.get_current_response_probability()
    result = random.random() < response_probability
    if result:
        logger.info("hit!")
    else:
        logger.info("skip.")
    return result


def is_hit_by_message_json(percent: int, json_data: Dict[str, Any]) -> bool:
    if json_data["isFirst"] or json_data["isFirstOnStream"]:
        # 初見さんや配信で初回の人への回答は必須
        percent = 100
    return is_hit(percent)
