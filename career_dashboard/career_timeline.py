from __future__ import annotations


def build_career_timeline(assets: list[dict], history: list[dict]) -> list[dict]:
    timeline = []
    if history:
        for item in history:
            timeline.append({
                'timestamp': item.get('timestamp', ''),
                'event': item.get('event_type', ''),
                'title': item.get('title', ''),
                'asset_type': item.get('asset_type', ''),
                'role': item.get('role', ''),
                'country': item.get('country', ''),
            })
    else:
        for asset in assets:
            timeline.append({
                'timestamp': asset.get('created_at', ''),
                'event': f"{asset.get('asset_type', '')}_created",
                'title': asset.get('title', ''),
                'asset_type': asset.get('asset_type', ''),
                'role': asset.get('role', ''),
                'country': asset.get('country', ''),
            })
    timeline.sort(key=lambda item: item.get('timestamp', ''), reverse=True)
    return timeline


def build_recent_activity(timeline: list[dict], limit: int = 10) -> list[dict]:
    return timeline[:limit]
