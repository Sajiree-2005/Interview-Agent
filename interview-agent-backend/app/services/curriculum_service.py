"""Curriculum data loading and access layer."""
import json
from typing import List, Dict, Any, Optional
from app.models.schemas import CurriculumData, CurriculumDay, CurriculumModule
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CurriculumService:
    """Service for loading and querying curriculum data."""

    def __init__(self):
        self._data: Optional[CurriculumData] = None
        self._day_map: Dict[int, CurriculumDay] = {}
        self._module_map: Dict[int, CurriculumModule] = {}
        self._topic_index: Dict[str, List[int]] = {}

    def load(self) -> "CurriculumService":
        """Load curriculum from JSON file."""
        settings = get_settings()
        try:
            with open(settings.curriculum_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._data = CurriculumData(**raw)
            self._build_indices()
            logger.info("curriculum_loaded", days=len(self._data.days), modules=len(self._data.modules))
        except Exception as e:
            logger.error("curriculum_load_failed", error=str(e))
            raise
        return self

    def _build_indices(self) -> None:
        """Build lookup indices for fast access."""
        for day in self._data.days:
            self._day_map[day.day] = day
            # Index by keywords in title
            words = day.title.lower().split()
            for word in words:
                if len(word) > 3:
                    self._topic_index.setdefault(word, []).append(day.day)
            # Index by tools
            for tool in day.tools:
                key = tool.lower()
                self._topic_index.setdefault(key, []).append(day.day)
        for mod in self._data.modules:
            self._module_map[mod.n] = mod

    @property
    def data(self) -> CurriculumData:
        if self._data is None:
            self.load()
        return self._data

    def get_day(self, day_num: int) -> Optional[CurriculumDay]:
        return self._day_map.get(day_num)

    def get_days_in_range(self, start: int, end: int) -> List[CurriculumDay]:
        return [self._day_map[d] for d in range(start, end + 1) if d in self._day_map]

    def get_all_days(self) -> List[CurriculumDay]:
        return self.data.days

    def get_module_for_day(self, day_num: int) -> Optional[CurriculumModule]:
        for mod in self.data.modules:
            if day_num in mod.days:
                return mod
        return None

    def get_module_days(self, module_n: int) -> List[int]:
        mod = self._module_map.get(module_n)
        return mod.days if mod else []

    def search_days_by_keyword(self, keyword: str) -> List[int]:
        return self._topic_index.get(keyword.lower(), [])

    def get_day_text_for_embedding(self, day: CurriculumDay) -> str:
        """Flatten a day into an embedding-friendly text."""
        lines = [
            f"Day {day.day}: {day.title}",
            f"Type: {day.type}",
            f"Tools: {', '.join(day.tools)}",
            "Objectives:",
        ]
        for obj in day.objectives:
            lines.append(f"  - {obj}")
        return "\n".join(lines)


# Singleton instance
curriculum_service = CurriculumService()
