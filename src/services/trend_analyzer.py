"""Trend Analyzer - Analyzes TikTok trends for script optimization."""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import yaml


class TrendAnalyzer:
    """Analyzes current TikTok trends and provides recommendations."""

    def __init__(self):
        self.config = self._load_config()
        self.trends = self.config.get('trends_january_2026', {})
        self.algorithm = self.config.get('algorithm', {})
        self.niches = self.config.get('niches', {})

    def _load_config(self) -> Dict:
        """Load configuration from viral_codes.yaml."""
        config_path = Path(__file__).parent.parent.parent / "config" / "viral_codes.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def get_current_trends(self) -> List[Dict]:
        """Get current trending formats for January 2026."""
        formats = self.trends.get('formats', [])
        return [
            {
                "name": f.get('name', ''),
                "description": f.get('description', ''),
                "template": f.get('template', ''),
                "popularity": 0.85  # Default high popularity for current trends
            }
            for f in formats
        ]

    def get_optimal_length(self, niche: str) -> int:
        """Get optimal video length for a niche."""
        if niche in self.niches:
            return self.niches[niche].get('optimal_length', 45)
        return self.algorithm.get('content_length', {}).get('optimal', 45)

    def get_niche_config(self, niche: str) -> Dict:
        """Get configuration for a specific niche."""
        return self.niches.get(niche, {
            "tone": "authentique",
            "hooks_preferred": ["curiosity_gap", "education"],
            "hashtags": [],
            "optimal_length": 45
        })

    def get_hashtags(self, niche: str, topic: str = "") -> List[str]:
        """Generate relevant hashtags for content."""
        base_hashtags = self.niches.get(niche, {}).get('hashtags', [])

        # Add topic-specific hashtags
        topic_words = topic.lower().split()[:3]
        topic_hashtags = [f"#{word}" for word in topic_words if len(word) > 3]

        # Combine and deduplicate
        all_hashtags = base_hashtags + topic_hashtags

        # Add trending January 2026 tags
        trending_tags = ["#2026", "#newyear"]

        return list(set(all_hashtags + trending_tags))[:8]

    def get_algorithm_tips(self) -> List[str]:
        """Get tips based on current algorithm priorities."""
        priorities = self.algorithm.get('priorities', [])
        tips = []

        for priority in priorities:
            if isinstance(priority, dict):
                for key, value in priority.items():
                    if key == 'completion_rate':
                        tips.append(f"Vise {int(value*100)}%+ de completion rate")
                    elif key == 'watch_time_ratio':
                        tips.append(f"Maintiens l'attention sur {int(value*100)}%+ de la vidéo")
                    elif key == 'original_audio' and value:
                        tips.append("Utilise ton propre audio plutôt que des sons trending")
                    elif key == 'return_viewers' and value:
                        tips.append("Fidélise ton audience avec des séries")

        return tips

    def get_best_posting_times(self) -> List[str]:
        """Get optimal posting times."""
        return self.algorithm.get('posting', {}).get('best_times', [
            "7h-9h", "12h-14h", "19h-22h"
        ])

    def get_anti_patterns(self) -> List[str]:
        """Get list of things to avoid."""
        return self.config.get('anti_patterns', [
            "#fyp #viral #foryou",
            "Première seconde sans hook",
            "Promesse non tenue"
        ])

    def analyze_topic(self, topic: str, niche: str) -> Dict:
        """Analyze a topic and provide recommendations."""
        niche_config = self.get_niche_config(niche)
        trends = self.get_current_trends()

        # Find matching trends
        matching_trends = []
        topic_lower = topic.lower()
        for trend in trends:
            if any(word in trend['name'].lower() for word in topic_lower.split()):
                matching_trends.append(trend)

        return {
            "optimal_length": self.get_optimal_length(niche),
            "recommended_tone": niche_config.get('tone', 'authentique'),
            "preferred_hooks": niche_config.get('hooks_preferred', []),
            "suggested_hashtags": self.get_hashtags(niche, topic),
            "matching_trends": matching_trends,
            "algorithm_tips": self.get_algorithm_tips(),
            "posting_times": self.get_best_posting_times(),
            "avoid": self.get_anti_patterns()[:5]
        }

    def score_script_potential(self, script_data: Dict) -> Dict:
        """Score the viral potential of a script."""
        score = 0
        factors = []

        # Check hook presence and strength
        if script_data.get('hook'):
            score += 25
            factors.append("Hook présent (+25)")

        # Check structure completeness
        sections = ['setup', 'content', 'payoff']
        for section in sections:
            if script_data.get(section):
                score += 15
                factors.append(f"{section.capitalize()} présent (+15)")

        # Check CTA
        if script_data.get('cta'):
            score += 10
            factors.append("CTA inclus (+10)")

        # Check duration optimization
        duration = script_data.get('duration', 45)
        sweet_spot = self.algorithm.get('content_length', {}).get('sweet_spot', [30, 60])
        if sweet_spot[0] <= duration <= sweet_spot[1]:
            score += 10
            factors.append("Durée optimale (+10)")

        # Determine rating
        if score >= 80:
            rating = "Excellent potentiel viral"
        elif score >= 60:
            rating = "Bon potentiel"
        elif score >= 40:
            rating = "Potentiel moyen"
        else:
            rating = "Amélioration nécessaire"

        return {
            "score": score,
            "max_score": 100,
            "rating": rating,
            "factors": factors
        }
