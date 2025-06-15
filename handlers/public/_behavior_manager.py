import re

from fuzzywuzzy import fuzz

from core.db_manager import DBManager
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("BehaviorManager")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

banned_behaviors = DBManager("moderator-db", "banned-behaviors")

class BehaviorManager:
    def __init__(self):
        self.fuzzy_treshold = 85
        self.trigger_level = 4

    async def check_offensive_behavior(self, message):
        """Check if the message contains any offensive behavior."""
        if not message:
            return False

        # Fetch all banned behaviors from the database
        banned_behaviors_list = await banned_behaviors.get_all_data_in_collection()
        if not banned_behaviors_list:
            _log.getLogger().debug("No banned behaviors found in the database.")
            return False

        for behavior in banned_behaviors_list[0]["patterns"]:
            match = re.search(behavior["text"], message, re.IGNORECASE)
            # _log.getLogger().debug(f"Checking behavior: {behavior['text']} against message: {message}")

            if match:
                matched_text = match.group(0)
                _log.getLogger().info(f"Found exact match {matched_text} for pattern: {behavior['text']}! Checking fuzzy match...")

                start, end = match.span()
                _log.getLogger().debug(f"Matched text: '{matched_text}' at position {start}-{end} in the message.")

                if match.groups():
                    _log.getLogger().debug(f"Matched groups: {match.groups()}")

                return True  # Return True immediately if an exact match is found

            # ratio = fuzz.ratio(message.lower(), matched_text.lower())
            # text = behavior["text"].split("()")
            # print(text)
            # ratio = fuzz.ratio(message.lower(), matched_text.lower())
            # _log.getLogger().debug(f"Fuzzy match ratio: {ratio} for behavior: {behavior['text']}")

            # if ratio >= self.fuzzy_treshold:
            #     _log.getLogger().info(f"Offensive behavior detected: {behavior['text']} with ratio {ratio}.")
            #     return True
                
                # if fuzz.partial_ratio(message.lower(), behavior["text"].lower()) >= self.fuzzy_treshold:
                #     _log.getLogger().info(f"Partial match for offensive behavior detected: {behavior['text']}")
                #     return True
                
                # if behavior["danger"] >= self.trigger_level:
                #     _log.getLogger().info(f"High danger level for behavior: {behavior['text']}, triggering action.")
                #     return True

        _log.getLogger().debug("No offensive behavior detected.")
        return False

    def set_behavior(self, new_behavior):
        self.behavior = new_behavior

    def reset_behavior(self):
        self.behavior = None