"""Script Generator - Core AI-powered script generation service."""

import json
import re
from typing import Dict, Optional, List
from pathlib import Path

from .hook_library import HookLibrary
from .trend_analyzer import TrendAnalyzer
from .claude_client import claude_client


class ScriptGenerator:
    """Generates viral TikTok scripts using Claude AI."""

    def __init__(self):
        self.hook_library = HookLibrary()
        self.trend_analyzer = TrendAnalyzer()
        self.claude = claude_client
        self.script_structure = self._load_structure()

    def _load_structure(self) -> Dict:
        """Load script structure from config."""
        config_path = Path(__file__).parent.parent.parent / "config" / "viral_codes.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('script_structure', {})
        return self._get_default_structure()

    def _get_default_structure(self) -> Dict:
        """Default script structure."""
        return {
            "hook": {"duration": [0, 3]},
            "setup": {"duration": [3, 15]},
            "content": {"duration": [15, 45]},
            "payoff": {"duration": [45, 55]},
            "cta": {"duration": [55, 60]}
        }

    def _get_duration_for_length(self, length: str) -> int:
        """Get target duration based on length preference."""
        durations = {
            "short": 25,
            "medium": 45,
            "long": 75
        }
        return durations.get(length, 45)

    def _build_prompt(self, request: Dict) -> str:
        """Build the Claude prompt for script generation."""
        topic = request.get('topic', '')
        niche = request.get('niche', 'custom')
        hook_style = request.get('hook_style', 'auto')
        length = request.get('length', 'medium')
        target_audience = request.get('target_audience', '')
        tone = request.get('tone', '')
        include_cta = request.get('include_cta', True)
        series_episode = request.get('series_episode')

        # Get analysis
        analysis = self.trend_analyzer.analyze_topic(topic, niche)
        duration = self._get_duration_for_length(length)

        # Determine hook style
        if hook_style == 'auto':
            hook_style = self.hook_library.get_best_hook_for_niche(niche)

        # Get a hook template for inspiration
        hook_template = self.hook_library.get_hook_template(hook_style, topic)

        prompt = f"""Tu es un expert en création de contenu viral TikTok. Génère un script complet pour une vidéo TikTok.

SUJET: {topic}
NICHE: {niche}
DURÉE CIBLE: {duration} secondes
STYLE DE HOOK: {hook_style}
{"AUDIENCE CIBLE: " + target_audience if target_audience else ""}
{"TONE: " + tone if tone else "TONE: " + analysis.get('recommended_tone', 'authentique')}
{"EPISODE " + str(series_episode) + " d'une série" if series_episode else ""}

INSPIRATION HOOK: "{hook_template}"

STRUCTURE OBLIGATOIRE (avec timecodes):

1. HOOK (0-3s): Accroche immédiate. Question choc ou statement provocateur. L'utilisateur doit être captivé INSTANTANÉMENT.

2. SETUP (3-{min(15, duration//4)}s): Contexte rapide. Établis la crédibilité ou l'enjeu. "Voici pourquoi..." ou "Ce que personne ne dit..."

3. CONTENT ({min(15, duration//4)}-{duration-15}s): Valeur principale. 3-5 points digestibles. Chaque phrase doit informer ou surprendre.

4. PAYOFF ({duration-15}-{duration-5}s): Climax. Résous la tension du hook. Moment de satisfaction ou révélation.

{"5. CTA (" + str(duration-5) + "-" + str(duration) + "s): Appel à l'action. 'Et toi?' / 'Tag quelqu'un' / 'Partie 2?'" if include_cta else ""}

RÈGLES ALGORITHME TIKTOK 2026:
- Completion rate > 80% = priorité
- Pas de #fyp ou #viral (inutile)
- Audio original > trending sounds
- Engagement dans la première heure crucial

ANTI-PATTERNS À ÉVITER:
{chr(10).join('- ' + ap for ap in analysis.get('avoid', [])[:5])}

Réponds UNIQUEMENT en JSON valide avec cette structure exacte:
{{
    "hook": {{
        "timecode": "0-3s",
        "text": "...",
        "visual_notes": "..."
    }},
    "setup": {{
        "timecode": "3-Xs",
        "text": "...",
        "visual_notes": "..."
    }},
    "content": {{
        "timecode": "X-Ys",
        "text": "...",
        "visual_notes": "..."
    }},
    "payoff": {{
        "timecode": "Y-Zs",
        "text": "...",
        "visual_notes": "..."
    }},
    {"\"cta\": { \"timecode\": \"Z-" + str(duration) + "s\", \"text\": \"...\", \"visual_notes\": \"...\" }," if include_cta else ""}
    "total_duration": {duration},
    "tips": ["conseil1", "conseil2", "conseil3"]
}}"""

        return prompt

    def _call_claude(self, prompt: str) -> Optional[str]:
        """Call Claude (API or CLI) to generate the script."""
        return self.claude.generate(prompt, max_tokens=2000)

    def _parse_response(self, response: str) -> Optional[Dict]:
        """Parse Claude's JSON response."""
        return self.claude.parse_json_response(response)

    def _generate_fallback_script(self, request: Dict) -> Dict:
        """Generate a fallback script without Claude."""
        topic = request.get('topic', 'ce sujet')
        niche = request.get('niche', 'custom')
        length = request.get('length', 'medium')
        hook_style = request.get('hook_style', 'auto')

        if hook_style == 'auto':
            hook_style = self.hook_library.get_best_hook_for_niche(niche)

        duration = self._get_duration_for_length(length)

        # Generate hook
        hook_context = {
            "topic": topic,
            "niche": niche,
            "duration": "30 jours",
            "number": 5
        }
        hook_text = self.hook_library.generate_hook(hook_style, hook_context)

        return {
            "hook": {
                "timecode": "0-3s",
                "text": hook_text,
                "visual_notes": "Face cam rapprochée, émotion surprise"
            },
            "setup": {
                "timecode": f"3-{min(15, duration//4)}s",
                "text": f"Voici ce que j'ai découvert sur {topic}...",
                "visual_notes": "Transition rapide, texte à l'écran"
            },
            "content": {
                "timecode": f"{min(15, duration//4)}-{duration-15}s",
                "text": f"Premier point important sur {topic}. Deuxième élément clé. Et surtout, le troisième aspect que tout le monde ignore.",
                "visual_notes": "Points numérotés à l'écran, B-roll dynamique"
            },
            "payoff": {
                "timecode": f"{duration-15}-{duration-5}s",
                "text": f"C'est pour ça que {topic} peut tout changer.",
                "visual_notes": "Moment de révélation, pause dramatique"
            },
            "cta": {
                "timecode": f"{duration-5}-{duration}s",
                "text": "Et toi, tu en penses quoi? Dis-moi en commentaire!",
                "visual_notes": "Pointer vers les commentaires"
            },
            "total_duration": duration,
            "tips": [
                "Filme en lumière naturelle",
                "Parle directement à la caméra",
                "Ajoute des sous-titres"
            ]
        }

    def generate(self, request: Dict) -> Dict:
        """Generate a complete viral TikTok script."""
        topic = request.get('topic', '')
        niche = request.get('niche', 'custom')
        hook_style = request.get('hook_style', 'auto')

        # Build and execute prompt
        prompt = self._build_prompt(request)
        response = self._call_claude(prompt)
        script_data = self._parse_response(response)

        # Use fallback if Claude fails
        if not script_data:
            script_data = self._generate_fallback_script(request)

        # Get hashtags and analysis
        hashtags = self.trend_analyzer.get_hashtags(niche, topic)

        # Calculate hook score
        if hook_style == 'auto':
            hook_style = self.hook_library.get_best_hook_for_niche(niche)
        hook_efficacy = self.hook_library.get_efficacy(hook_style)
        hook_score = round(hook_efficacy * 10, 1)

        # Score viral potential
        potential = self.trend_analyzer.score_script_potential({
            "hook": script_data.get('hook'),
            "setup": script_data.get('setup'),
            "content": script_data.get('content'),
            "payoff": script_data.get('payoff'),
            "cta": script_data.get('cta'),
            "duration": script_data.get('total_duration', 45)
        })

        return {
            "success": True,
            "script": {
                "hook": script_data.get('hook', {}),
                "setup": script_data.get('setup', {}),
                "content": script_data.get('content', {}),
                "payoff": script_data.get('payoff', {}),
                "cta": script_data.get('cta'),
                "total_duration": script_data.get('total_duration', 45),
                "hashtags": hashtags,
                "hook_score": hook_score,
                "viral_potential": potential.get('rating', 'Bon potentiel'),
                "tips": script_data.get('tips', [])
            }
        }
