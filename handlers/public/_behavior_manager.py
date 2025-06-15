import re
from typing import List, Dict, Tuple

from fuzzywuzzy import fuzz

from core.db_manager import DBManager
from logger import Log, STANDARD_LOG_LEVEL

_log = Log("BehaviorManager")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

banned_behaviors = DBManager("moderator-db", "banned-behaviors")
_cached_patterns: List[Dict] = []  # Cache for patterns to avoid repeated database calls

class BehaviorManager:
    def __init__(self):
        self.fuzzy_treshold = 85
        self.trigger_level = 4

    async def check_offensive_behavior(self, message):
        """Check if the message contains any offensive behavior."""
        if not message:
            return "", False

        # Fetch all banned behaviors from the database
        banned_behaviors_list = await self._load_patterns()
        if not banned_behaviors_list:
            _log.getLogger().debug("No banned behaviors found in the database.")
            return "", False

        for behavior in banned_behaviors_list:
            match = re.search(behavior["text"], message, re.IGNORECASE)

            if match:
                matched_text = match.group(0)
                _log.getLogger().info(f"Found exact match {matched_text} for pattern: {behavior['text']}")

                start, end = match.span()
                _log.getLogger().debug(f"Matched text: '{matched_text}' at position {start}-{end} in the message.")

                if match.groups():
                    _log.getLogger().debug(f"Matched groups: {match.groups()}")

                return "re.search", True  # Return True immediately if an exact match is found

        result, score = self.find_best_pattern_match(message, banned_behaviors_list)
        if result:
            _log.getLogger().info(f"Fuzzy match found: {result['text']} with score {score}.")
            _log.getLogger().debug(f"Matched text: '{result['text']}' with score {score} in the message.")
            return "fuzzywuzzy", True
        
        _log.getLogger().debug("No offensive behavior detected.")
        return "", False

    def _expand_pattern(self, pattern: str) -> List[str]:
        """Expand the behavior text to include variations."""
        match = re.findall(r"\(([^()]+)\)", pattern)
        if not match:
            return [pattern]

        variants = []
        for group in match:
            parts = group.split("|")
            variants.append(parts)

        # Build all combinations of the pattern with the variants
        def build_options(base: str, parts: List[List[str]]) -> List[str]:
            """Recursively build all combinations of the base pattern with the variants."""
            results = [base]
            for group in parts:
                new_results = []
                for prefix in results:
                    for part in group:
                        new_results.append(re.sub(r"\([^()]+\)", part, prefix, count=1))
                results = new_results
            return results
        
        return build_options(pattern, variants)
    
    def find_best_pattern_match(self, text: str, patterns: List[Dict]) -> Tuple[Dict, int]:
        matches = []
        for pattern in patterns:
            options = self._expand_pattern(pattern["text"])
            for opt in options:
                score = fuzz.partial_ratio(opt.lower(), text.lower())
                if score >= self.fuzzy_treshold:
                    matches.append((pattern, score))

        if not matches:
            return ({}, 0)

        # Find the pattern with the highest score
        best = max(matches, key=lambda x: x[1])
        return best  # (pattern_dict, score)
    
    async def _load_patterns(self):
        """Load patterns from the database and cache them."""
        global _cached_patterns
        if not _cached_patterns:
            _cached_patterns = await banned_behaviors.get_all_data_in_collection()
            if not _cached_patterns:
                _log.getLogger().debug("No patterns found in the database.")
            else:
                _log.getLogger().debug(f"Loaded {len(_cached_patterns[0]['patterns'])} patterns from the database.")
        return _cached_patterns[0]["patterns"] if _cached_patterns else []
    