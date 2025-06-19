import re
from typing import List, Tuple

from pyrogram.enums import MessageEntityType

from fuzzywuzzy import fuzz

from logger import Log 
from constants import STANDARD_LOG_LEVEL

_log = Log("AdDetector")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

AD_KEYWORDS = [
    "подпишись", "вступай", "переходи", "ссылка в описании",
    "зарегистрируйся", "узнай больше", "получи деньги",
    "зараб(отай|атывать|атывай)", "прибыль", "скидка", "акция", "промокод",
    "бот", "нажми", "получи бонус"
]

# AD_KEYWORDS = [
#     "подпишись", "вступай", "переходи", "ссылка в описании",
#     "зарегистрируйся", "узнай больше", "получи деньги",
#     "заработай", "прибыль", "скидка", "акция", "промокод",
#     "бот", "нажми", "получи бонус"
# ]

class AdDetector:

    def __init__(self):
        self.matched_keywords: List[str] = []
        self.fuzzy_hits: List[Tuple[str, int]] = []

        self.URL_PATTERN = re.compile(r"(https?://\S+|t\.me/\S+|@\w+|www\.\S+)", re.IGNORECASE)
        self.FUZZY_THRESHOLD = 85

    def detect_ad_message(self, msg) -> Tuple[str, str, bool]:
        _log.getLogger().debug("Start detecting ads...")

        text = getattr(msg, "text", None)
        entities = getattr(msg, "entities", None)

        method = ""
        for kw in AD_KEYWORDS:
            if re.search(kw, text, flags=re.IGNORECASE):
                method += "re.search"
                self.matched_keywords.append(kw)

            score = fuzz.partial_ratio(kw.lower(), text.lower())
            if score >= self.FUZZY_THRESHOLD:
                method += "fuzzywuzzy"
                self.fuzzy_hits.append((kw, score))

        has_link = bool(self.URL_PATTERN.search(text))

        if self.matched_keywords or self.fuzzy_hits or has_link or entities:
            reason = ""
            if has_link:
                reason += "Содержит ссылку. "
            if entities:
                for entity in entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        reason += f"Содержит вложенную ссылку на {entity.url}"
            if self.matched_keywords:
                reason += f"Ключевые слова: {', '.join(self.matched_keywords)}. "
            if self.fuzzy_hits:
                fuzzy_str = ", ".join([f"{kw} ({score})" for kw, score in self.fuzzy_hits])
                reason += f"Похожие выражения: {fuzzy_str}."

            return reason, method, True

        return None, None, False
    