"""Pydantic models for the TikTok Viral Script Generator API."""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class Niche(str, Enum):
    """Available content niches."""
    FINANCE = "finance"
    FITNESS = "fitness"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    COMEDY = "comedy"
    EDUCATION = "education"
    CUSTOM = "custom"


class HookStyle(str, Enum):
    """Types of hooks for viral content."""
    CONTROVERSY = "controversy"
    CURIOSITY_GAP = "curiosity_gap"
    FEAR_OF_MISSING = "fear_of_missing"
    STORY_LOOP = "story_loop"
    CONFESSION = "confession"
    EDUCATION = "education"
    TRANSFORMATION = "transformation"
    AUTO = "auto"


class ScriptLength(str, Enum):
    """Video duration options."""
    SHORT = "short"      # 15-30s
    MEDIUM = "medium"    # 30-60s
    LONG = "long"        # 60-90s


class ScriptRequest(BaseModel):
    """Request model for script generation."""
    topic: str = Field(..., min_length=3, max_length=500, description="Main topic of the video")
    niche: Niche = Field(default=Niche.CUSTOM, description="Content niche")
    hook_style: HookStyle = Field(default=HookStyle.AUTO, description="Preferred hook style")
    length: ScriptLength = Field(default=ScriptLength.MEDIUM, description="Target video length")
    target_audience: Optional[str] = Field(None, max_length=200, description="Target audience description")
    tone: Optional[str] = Field(None, max_length=100, description="Desired tone (e.g., funny, serious, motivating)")
    include_cta: bool = Field(default=True, description="Include call-to-action")
    series_episode: Optional[int] = Field(None, ge=1, le=10, description="Episode number if part of a series")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Comment j'ai gagné 5000€ en side hustle",
                "niche": "business",
                "hook_style": "confession",
                "length": "medium",
                "target_audience": "jeunes entrepreneurs 20-35 ans",
                "tone": "authentique et motivant",
                "include_cta": True
            }
        }


class ScriptSection(BaseModel):
    """A section of the generated script."""
    name: str = Field(..., description="Section name (hook, setup, content, payoff, cta)")
    timecode: str = Field(..., description="Timecode range (e.g., '0-3s')")
    text: str = Field(..., description="Script text for this section")
    visual_notes: Optional[str] = Field(None, description="Visual/editing suggestions")


class GeneratedScript(BaseModel):
    """The complete generated script."""
    hook: ScriptSection
    setup: ScriptSection
    content: ScriptSection
    payoff: ScriptSection
    cta: Optional[ScriptSection] = None

    total_duration: int = Field(..., description="Estimated duration in seconds")
    hashtags: List[str] = Field(default_factory=list, description="Suggested hashtags")
    hook_score: float = Field(..., ge=0, le=10, description="Hook effectiveness score")
    viral_potential: str = Field(..., description="Viral potential rating")
    tips: List[str] = Field(default_factory=list, description="Additional tips for the creator")


class ScriptResponse(BaseModel):
    """API response containing the generated script."""
    success: bool
    script: Optional[GeneratedScript] = None
    error: Optional[str] = None
    generation_time_ms: int = Field(..., description="Time taken to generate in milliseconds")


class TrendInfo(BaseModel):
    """Information about a current trend."""
    name: str
    description: str
    template: str
    popularity: float = Field(..., ge=0, le=1)
    recommended_niches: List[str]


class TrendsResponse(BaseModel):
    """Response containing current trends."""
    trends: List[TrendInfo]
    last_updated: str
    source: str = "TikTok Viral Codes 2026"
