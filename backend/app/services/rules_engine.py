# Sentinel-X Rules Engine
# Automated decision-making based on events

import yaml
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ActionType(str, Enum):
    ALERT = "alert"
    LOCK = "lock"
    NOTIFY = "notify"
    RECORD = "record"
    IGNORE = "ignore"

@dataclass
class Rule:
    """A single decision rule."""
    name: str
    condition: str
    action: ActionType
    params: Dict
    enabled: bool = True

class RulesEngine:
    """Evaluates events against rules to make autonomous decisions."""

    def __init__(self, config_path: str = "config/rules.yaml"):
        self.config_path = config_path
        self.rules: List[Rule] = []
        self.load_rules()

    def load_rules(self):
        """Load rules from YAML config."""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            for rule_data in config.get('rules', []):
                rule = Rule(**rule_data)
                self.rules.append(rule)
            logger.info(f"Loaded {len(self.rules)} rules")
        except FileNotFoundError:
            logger.warning(f"Rules file not found: {self.config_path}")
            self.rules = self._default_rules()

    def _default_rules(self) -> List[Rule]:
        """Default rules if config file is missing."""
        return [
            Rule(
                name="motion_at_night",
                condition="event_type == 'motion' and hour >= 18 and hour <= 6",
                action=ActionType.ALERT,
                params={"severity": "high", "channels": ["telegram", "email"]}
            ),
            Rule(
                name="person_detected",
                condition="event_type == 'detection' and class == 'person'",
                action=ActionType.RECORD,
                params={"duration": 30}
            ),
            Rule(
                name="vehicle_detected",
                condition="event_type == 'detection' and class == 'vehicle'",
                action=ActionType.NOTIFY,
                params={"severity": "medium"}
            ),
            Rule(
                name="high_motion_frequency",
                condition="event_type == 'motion' and count_last_5min > 5",
                action=ActionType.ALERT,
                params={"severity": "critical", "channels": ["telegram", "email", "siren"]}
            ),
        ]

    def evaluate(self, event: Dict) -> List[Rule]:
        """Evaluate an event against all rules."""
        matched_rules = []
        for rule in self.rules:
            if not rule.enabled:
                continue
            if self._evaluate_condition(rule.condition, event):
                matched_rules.append(rule)
        return matched_rules

    def _evaluate_condition(self, condition: str, event: Dict) -> bool:
        """Evaluate a condition string against an event."""
        try:
            # Simple condition evaluation
            local_vars = {**event, 'hour': event.get('timestamp', 0) % 24}
            return eval(condition, {"__builtins__": {}}, local_vars)
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False