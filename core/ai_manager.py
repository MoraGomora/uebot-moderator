from openai import AsyncOpenAI
from typing import List, Dict

from config import config
from logger import Log, STANDARD_LOG_LEVEL
from handlers.public._actions import ModDecision, ModAction

from ._prompt_manager import get_prompt
from enums import ModerationMode

_log = Log("AIManager")
_log.getLogger().setLevel(STANDARD_LOG_LEVEL)
_log.write_logs_to_file()

class AIManager:
    def __init__(self):
        _key = config.get_ionet_key()
        if not isinstance(_key, str):
            raise TypeError("API key must be a string")

        self._client = AsyncOpenAI(
            api_key=_key,
            base_url="https://api.intelligence.io.solutions/api/v1/"
        )

        _log.getLogger().debug("AIManager initialized with OpenAI client")
        if not isinstance(self._client, AsyncOpenAI):
            raise TypeError("Client must be an instance of AsyncOpenAI")

        self._system_prompt = get_prompt(ModerationMode.TOXICITY)
        self.messages = [{"role": "system", "content": self._system_prompt}]

    async def analyze_message(self, message: str, model: str = "meta-llama/Llama-3.3-70B-Instruct") -> ModDecision:
        try:
            if not isinstance(self.messages, List) or not all(isinstance(m, Dict) for m in self.messages):
                raise TypeError("messages must be a list of dictionaries")
            
            if message:
                self.messages.append({"role": "user", "content": f"Analyze this message: {message}"})

            _log.getLogger().debug("Starting to analyse the message...")

            response = await self._client.chat.completions.create(
                model=model,
                messages=self.messages,
                temperature=0.7,
                stream=False,
                max_completion_tokens=200
            )

            _log.getLogger().debug(f"Response generated: {response.choices[0].message.content}")
            if not response or not response.choices or not response.choices[0].message:
                raise ValueError("Invalid response format from AI model")

            response_text = response.choices[0].message.content
            decision = self._parse_response(response_text)
            _log.getLogger().debug(f"Moderation decision: {decision}")

            return decision
        except Exception as e:
            _log.getLogger().error(f"Error generating response: {str(e)}")
            return ModDecision(
                action=ModAction.NONE,
                reason="Error processing message: " + str(e),
                confidence=0.0
            )

    async def analyze_message_context(self, messages: List, method: str, model: str = "meta-llama/Llama-3.3-70B-Instruct") -> ModDecision:
        try:
            if not isinstance(messages, List) or not all(isinstance(m, Dict) for m in self.messages):
                raise TypeError("messages must be a list of dictionaries")
            
            if messages:
                self.messages.append({"role": "user", "content": f"Analyze these messages context: {messages} and make a decision by prompt! Analyzed by {method}"})

            _log.getLogger().debug("Starting to analyse the message...")
            print(self.messages)

            response = await self._client.chat.completions.create(
                model=model,
                messages=self.messages,
                temperature=0.7,
                stream=False,
                max_completion_tokens=200
            )

            if not response or not response.choices or not response.choices[0].message:
                raise ValueError("Invalid response format from AI model")

            response_text = response.choices[0].message.content
            decision = self._parse_response(response_text)
            _log.getLogger().debug(f"Moderation decision: {decision}")

            return decision
        except Exception as e:
            _log.getLogger().error(f"Error generating response: {str(e)}")
            return ModDecision(
                action=ModAction.NONE,
                reason="Error processing message: " + str(e),
                confidence=0.0
            )
        
    def _parse_response(self, response_text: str) -> ModDecision:
        lines = response_text.strip().split("\n")
        decision_data = {}

        try:
            for line in lines:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    decision_data[key.strip().upper()] = value.strip()

            return ModDecision(
                action=ModAction(decision_data.get("ACTION", "none")),
                reason=decision_data.get("REASON", "No reason provided"),
                duration=int(decision_data.get("DURATION", 0)),
                warning_text=decision_data.get("WARNING"),
                confidence=float(decision_data.get("CONFIDENCE", 0.0))
            )
        except Exception as e:
            _log.getLogger().error(f"Error parsing response: {str(e)}")
            raise ValueError("Invalid response format from AI model")
        
    def update_system_prompt(self, new_rules: str):
        if not isinstance(new_rules, str):
            raise TypeError("new_prompt must be a string")
        if not self._system_prompt:
            raise ValueError("System prompt is not initialized")
        
        self._system_prompt += f"\n\nAdditional chat rules:\n{new_rules}"
        _log.getLogger().debug(f"Updating system prompt with new rules: {new_rules}")

    def change_moderation_mode(self, mode: ModerationMode):
        self._system_prompt = get_prompt(mode)
        _log.getLogger().debug(f"Change moderation mode to: {mode}")
