"""API Routes for TikTok Viral Script Generator."""

import time
from fastapi import APIRouter, HTTPException, Request
from typing import Optional

from .models import (
    ScriptRequest,
    ScriptResponse,
    TrendsResponse,
    TrendInfo,
    GeneratedScript,
    ScriptSection
)
from ..services import ScriptGenerator, TrendAnalyzer, HookLibrary
from ..services.trends_scraper import trends_scraper


router = APIRouter()

# Initialize services
script_generator = ScriptGenerator()
trend_analyzer = TrendAnalyzer()
hook_library = HookLibrary()


@router.post("/generate", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest) -> ScriptResponse:
    """Generate a viral TikTok script based on the provided parameters."""
    start_time = time.time()

    try:
        # Convert request to dict
        request_dict = {
            "topic": request.topic,
            "niche": request.niche.value,
            "hook_style": request.hook_style.value,
            "length": request.length.value,
            "target_audience": request.target_audience,
            "tone": request.tone,
            "include_cta": request.include_cta,
            "series_episode": request.series_episode
        }

        # Generate script
        result = script_generator.generate(request_dict)

        if not result.get('success'):
            raise HTTPException(status_code=500, detail="Script generation failed")

        script_data = result['script']

        # Build response
        generated_script = GeneratedScript(
            hook=ScriptSection(
                name="hook",
                timecode=script_data['hook'].get('timecode', '0-3s'),
                text=script_data['hook'].get('text', ''),
                visual_notes=script_data['hook'].get('visual_notes')
            ),
            setup=ScriptSection(
                name="setup",
                timecode=script_data['setup'].get('timecode', '3-15s'),
                text=script_data['setup'].get('text', ''),
                visual_notes=script_data['setup'].get('visual_notes')
            ),
            content=ScriptSection(
                name="content",
                timecode=script_data['content'].get('timecode', '15-45s'),
                text=script_data['content'].get('text', ''),
                visual_notes=script_data['content'].get('visual_notes')
            ),
            payoff=ScriptSection(
                name="payoff",
                timecode=script_data['payoff'].get('timecode', '45-55s'),
                text=script_data['payoff'].get('text', ''),
                visual_notes=script_data['payoff'].get('visual_notes')
            ),
            cta=ScriptSection(
                name="cta",
                timecode=script_data['cta'].get('timecode', '55-60s'),
                text=script_data['cta'].get('text', ''),
                visual_notes=script_data['cta'].get('visual_notes')
            ) if script_data.get('cta') else None,
            total_duration=script_data.get('total_duration', 45),
            hashtags=script_data.get('hashtags', []),
            hook_score=script_data.get('hook_score', 7.5),
            viral_potential=script_data.get('viral_potential', 'Bon potentiel'),
            tips=script_data.get('tips', [])
        )

        generation_time = int((time.time() - start_time) * 1000)

        return ScriptResponse(
            success=True,
            script=generated_script,
            generation_time_ms=generation_time
        )

    except Exception as e:
        generation_time = int((time.time() - start_time) * 1000)
        return ScriptResponse(
            success=False,
            error=str(e),
            generation_time_ms=generation_time
        )


@router.get("/trends", response_model=TrendsResponse)
async def get_trends() -> TrendsResponse:
    """Get current TikTok trends for January 2026."""
    trends = trend_analyzer.get_current_trends()

    trend_infos = [
        TrendInfo(
            name=t.get('name', ''),
            description=t.get('description', ''),
            template=t.get('template', ''),
            popularity=t.get('popularity', 0.5),
            recommended_niches=["business", "lifestyle", "education"]
        )
        for t in trends
    ]

    return TrendsResponse(
        trends=trend_infos,
        last_updated="2026-02-02",
        source="TikTok Viral Codes 2026"
    )


@router.get("/trends/live")
async def get_live_trends(request: Request, ip: Optional[str] = None):
    """
    Get live trending topics from X, TikTok, and Google.
    Automatically detects location from IP.
    """
    # Get client IP if not provided
    if not ip:
        ip = request.client.host if request.client else None
        # Handle localhost/forwarded IPs
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()

    try:
        data = await trends_scraper.get_all_trends(ip)
        return {
            "success": True,
            "location": data["location"],
            "updated_at": data["updated_at"],
            "trends": data["trends"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "trends": {
                "tiktok": [],
                "x": [],
                "google": [],
                "merged": []
            }
        }


@router.get("/location")
async def get_location(request: Request, ip: Optional[str] = None):
    """Detect user location from IP."""
    if not ip:
        ip = request.client.host if request.client else None
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()

    location = await trends_scraper.get_location_from_ip(ip)
    return {"success": True, "location": location}


@router.get("/hooks")
async def get_hook_styles():
    """Get available hook styles and their efficacy."""
    styles = hook_library.get_all_styles()
    return {
        "styles": [
            {
                "name": style,
                "efficacy": hook_library.get_efficacy(style),
                "template_example": hook_library.get_hook_template(style)
            }
            for style in styles
        ]
    }


@router.get("/niches")
async def get_niches():
    """Get available niches with their configurations."""
    niches = ["finance", "fitness", "lifestyle", "business", "comedy", "education"]
    return {
        "niches": [
            {
                "name": niche,
                "config": trend_analyzer.get_niche_config(niche),
                "best_hook": hook_library.get_best_hook_for_niche(niche)
            }
            for niche in niches
        ]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    from ..services.claude_client import claude_client
    return {
        "status": "healthy",
        "version": "1.1.0",
        "ai_mode": claude_client.get_mode(),
        "ai_available": claude_client.is_available()
    }
