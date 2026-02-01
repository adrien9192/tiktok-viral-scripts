"""Hook Library - Collection of viral hooks for TikTok scripts."""

import random
from typing import List, Dict, Optional
from pathlib import Path
import yaml


class HookLibrary:
    """Library of viral hooks categorized by type and niche."""

    def __init__(self):
        self.hooks = self._load_hooks()

    def _load_hooks(self) -> Dict:
        """Load hooks from viral_codes.yaml."""
        config_path = Path(__file__).parent.parent.parent / "config" / "viral_codes.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('hooks', {})
        return self._get_default_hooks()

    def _get_default_hooks(self) -> Dict:
        """Fallback hooks if config not found."""
        return {
            "controversy": {
                "templates": [
                    "Ce que {industry} ne veut pas que tu saches sur {topic}",
                    "Pourquoi personne ne parle de {hidden_truth}",
                ],
                "efficacy": 0.95
            },
            "curiosity_gap": {
                "templates": [
                    "J'ai enfin compris pourquoi {unexpected_result}",
                    "Ce qui se passe quand tu {action} pendant {duration}",
                ],
                "efficacy": 0.92
            },
            "confession": {
                "templates": [
                    "J'aurais jamais dû partager ça mais...",
                    "La vraie raison pour laquelle j'ai {action}",
                ],
                "efficacy": 0.90
            },
            "education": {
                "templates": [
                    "{profession} ici. Voici ce qu'on ne vous dit pas sur {topic}",
                    "En {duration}, tu vas apprendre {skill}",
                ],
                "efficacy": 0.87
            },
            "fear_of_missing": {
                "templates": [
                    "Si tu fais encore {mistake}, arrête immédiatement",
                    "Les {number} erreurs qui ruinent ton {goal}",
                ],
                "efficacy": 0.88
            },
            "story_loop": {
                "templates": [
                    "Jour {number} de {challenge}...",
                    "Episode {number}: Comment {journey}",
                ],
                "efficacy": 0.85
            },
            "transformation": {
                "templates": [
                    "De {before_state} à {after_state} en {duration}",
                    "Comment j'ai {achievement} sans {common_method}",
                ],
                "efficacy": 0.89
            }
        }

    def get_hook_template(self, style: str, topic: str = "") -> str:
        """Get a hook template for the given style."""
        if style not in self.hooks:
            style = random.choice(list(self.hooks.keys()))

        templates = self.hooks[style].get('templates', [])
        if not templates:
            return f"Découvre {topic}..."

        return random.choice(templates)

    def get_best_hook_for_niche(self, niche: str) -> str:
        """Get the most effective hook style for a niche."""
        niche_preferences = {
            "finance": ["confession", "education", "fear_of_missing"],
            "fitness": ["transformation", "education", "story_loop"],
            "lifestyle": ["confession", "curiosity_gap", "story_loop"],
            "business": ["education", "controversy", "fear_of_missing"],
            "comedy": ["curiosity_gap", "story_loop"],
            "education": ["education", "curiosity_gap", "controversy"],
        }
        preferred = niche_preferences.get(niche, list(self.hooks.keys()))
        return preferred[0] if preferred else "curiosity_gap"

    def get_all_styles(self) -> List[str]:
        """Get all available hook styles."""
        return list(self.hooks.keys())

    def get_efficacy(self, style: str) -> float:
        """Get the efficacy rating for a hook style."""
        if style in self.hooks:
            return self.hooks[style].get('efficacy', 0.5)
        return 0.5

    def generate_hook(self, style: str, context: Dict) -> str:
        """Generate a hook by filling in template placeholders."""
        template = self.get_hook_template(style)

        # Fill in placeholders with context
        replacements = {
            "{topic}": context.get("topic", "ce sujet"),
            "{industry}": context.get("niche", "l'industrie"),
            "{hidden_truth}": context.get("topic", "cette vérité"),
            "{unexpected_result}": context.get("topic", "ça"),
            "{action}": context.get("action", "ça"),
            "{duration}": context.get("duration", "30 jours"),
            "{profession}": context.get("profession", "Expert"),
            "{skill}": context.get("topic", "cette compétence"),
            "{mistake}": context.get("mistake", "cette erreur"),
            "{number}": str(context.get("number", 5)),
            "{goal}": context.get("goal", "ton objectif"),
            "{challenge}": context.get("topic", "ce challenge"),
            "{journey}": context.get("topic", "mon parcours"),
            "{before_state}": context.get("before", "0"),
            "{after_state}": context.get("after", "réussite"),
            "{achievement}": context.get("topic", "réussi"),
            "{common_method}": context.get("common_method", "la méthode classique"),
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        return result
