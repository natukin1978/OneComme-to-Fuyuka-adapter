import asyncio
import logging
import time
from typing import Any, Dict

import global_value as g

logger = logging.getLogger(__name__)

# --- 設定パラメータ ---
ALPHA: float = 0.01  # EMAの平滑化係数
MAX_FREQUENCY: float = 0.05  # 頻度調整の基準値 (1秒あたりnコメント)
FREQUENCY_INTERVAL_SECONDS: int = 1  # 頻度を計測する間隔

# --- 状態管理変数 ---
# 外部からアクセスされるため、クラスまたはモジュールレベルで管理
_comment_count_in_interval: int = 0  # 直近のインターバルで受け取ったコメント数
_exponential_moving_average: float = 0.0  # コメント頻度のEMA


# 基本の応答確率
def getBaseProbability() -> float:
    return g.config["fuyukaApi"]["answerLevel"] / 100


# 最小応答確率
def getMinProbability() -> float:
    return getBaseProbability() / 10


def increment_comment_count():
    """
    外部（メインボット）からコメントを受信した際に呼び出す関数。
    コメント数を1増やします。
    """
    global _comment_count_in_interval
    _comment_count_in_interval += 1


def get_current_response_probability() -> float:
    """
    現在のEMAに基づいて、AIの応答確率を計算します。
    """
    global _exponential_moving_average

    ema = _exponential_moving_average

    # 頻度がMAX_FREQUENCYに対してどの程度かを示す比率 (0.0 ～ 1.0)
    frequency_ratio = min(ema / MAX_FREQUENCY, 1.0)

    # getBaseProbability()をfrequency_ratioに応じて減らす
    adjusted_probability = getBaseProbability() * (1.0 - frequency_ratio)

    # 最小確率を下回らないように調整
    final_probability = max(getMinProbability(), adjusted_probability)

    return final_probability


async def start_frequency_monitor():
    """
    定期的にコメント頻度を計算し、EMAを更新するメインの非同期タスク。
    メインボットの起動時に一度だけ呼び出されます。
    """
    global _comment_count_in_interval, _exponential_moving_average

    logger.debug(
        f"[{__name__}] 頻度監視を開始。インターバル: {FREQUENCY_INTERVAL_SECONDS}秒"
    )

    while True:
        await asyncio.sleep(FREQUENCY_INTERVAL_SECONDS)

        # 1. 現在の頻度を計算 (1秒あたり)
        current_frequency = _comment_count_in_interval / FREQUENCY_INTERVAL_SECONDS

        # 2. EMAを更新
        if _exponential_moving_average == 0.0 and current_frequency > 0:
            # 初期化 (最初の非ゼロの頻度で初期化)
            _exponential_moving_average = current_frequency
        else:
            # EMA計算: EMA_new = alpha * Current_Frequency + (1 - alpha) * EMA_old
            _exponential_moving_average = (ALPHA * current_frequency) + (
                (1 - ALPHA) * _exponential_moving_average
            )

        # 3. カウンタをリセット
        _comment_count_in_interval = 0

        # ログ出力 (任意)
        current_prob = get_current_response_probability()
        logger.debug(
            f"[{time.strftime('%H:%M:%S', time.localtime())}] Freq: {current_frequency:.2f} msg/s | EMA: {_exponential_moving_average:.3f} | Prob: {current_prob*100:.2f}%"
        )
