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

        # Build anti-patterns list (avoid backslash in f-string)
        anti_patterns = analysis.get('avoid', [])[:5]
        newline = "\n"
        anti_patterns_text = newline.join("- " + ap for ap in anti_patterns)

        # Build optional sections
        audience_line = "AUDIENCE CIBLE: " + target_audience if target_audience else ""
        tone_value = tone if tone else analysis.get('recommended_tone', 'authentique')
        tone_line = "TONE: " + tone_value
        episode_line = "EPISODE " + str(series_episode) + " d'une série" if series_episode else ""

        setup_end = min(15, duration // 4)
        content_start = setup_end
        content_end = duration - 15
        payoff_end = duration - 5

        cta_section = "5. CTA (" + str(payoff_end) + "-" + str(duration) + "s): Appel à l'action." if include_cta else ""
        cta_json = '"cta": { "timecode": "' + str(payoff_end) + '-' + str(duration) + 's", "text": "...", "visual_notes": "..." },' if include_cta else ""

        prompt = """Tu es un expert en création de contenu viral TikTok. Génère un script complet pour une vidéo TikTok.

SUJET: """ + topic + """
NICHE: """ + niche + """
DURÉE CIBLE: """ + str(duration) + """ secondes
STYLE DE HOOK: """ + hook_style + """
""" + audience_line + """
""" + tone_line + """
""" + episode_line + """

INSPIRATION HOOK: \"""" + hook_template + """\"

STRUCTURE OBLIGATOIRE (avec timecodes):

1. HOOK (0-3s): Accroche immédiate. Question choc ou statement provocateur.

2. SETUP (3-""" + str(setup_end) + """s): Contexte rapide. "Voici pourquoi..." ou "Ce que personne ne dit..."

3. CONTENT (""" + str(content_start) + """-""" + str(content_end) + """s): Valeur principale. 3-5 points digestibles.

4. PAYOFF (""" + str(content_end) + """-""" + str(payoff_end) + """s): Climax. Résous la tension du hook.

""" + cta_section + """

RÈGLES ALGORITHME TIKTOK 2026:
- Completion rate > 80% = priorité
- Pas de #fyp ou #viral (inutile)
- Audio original > trending sounds

ANTI-PATTERNS À ÉVITER:
""" + anti_patterns_text + """

Réponds UNIQUEMENT en JSON valide:
{
    "hook": {
        "timecode": "0-3s",
        "text": "...",
        "visual_notes": "..."
    },
    "setup": {
        "timecode": "3-""" + str(setup_end) + """s",
        "text": "...",
        "visual_notes": "..."
    },
    "content": {
        "timecode": \"""" + str(content_start) + """-""" + str(content_end) + """s",
        "text": "...",
        "visual_notes": "..."
    },
    "payoff": {
        "timecode": \"""" + str(content_end) + """-""" + str(payoff_end) + """s",
        "text": "...",
        "visual_notes": "..."
    },
    """ + cta_json + """
    "total_duration": """ + str(duration) + """,
    "tips": ["conseil1", "conseil2", "conseil3"]
}"""

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

        setup_end = min(15, duration // 4)
        content_end = duration - 15
        payoff_end = duration - 5

        return {
            "hook": {
                "timecode": "0-3s",
                "text": hook_text,
                "visual_notes": "Face cam rapprochée, émotion surprise"
            },
            "setup": {
                "timecode": "3-" + str(setup_end) + "s",
                "text": "Voici ce que j'ai découvert sur " + topic + "...",
                "visual_notes": "Transition rapide, texte à l'écran"
            },
            "content": {
                "timecode": str(setup_end) + "-" + str(content_end) + "s",
                "text": "Premier point important sur " + topic + ". Deuxième élément clé. Et surtout, le troisième aspect que tout le monde ignore.",
                "visual_notes": "Points numérotés à l'écran, B-roll dynamique"
            },
            "payoff": {
                "timecode": str(content_end) + "-" + str(payoff_end) + "s",
                "text": "C'est pour ça que " + topic + " peut tout changer.",
                "visual_notes": "Moment de révélation, pause dramatique"
            },
            "cta": {
                "timecode": str(payoff_end) + "-" + str(duration) + "s",
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
