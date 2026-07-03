from __future__ import annotations


def build_version_key(asset_type: str, full_name: str = '', role: str = '', country: str = '') -> str:
    return '|'.join([
        str(asset_type or '').strip().lower(),
        str(full_name or '').strip().lower(),
        str(role or '').strip().lower(),
        str(country or '').strip().lower(),
    ])


def next_version(existing_assets: list[dict], asset_type: str, full_name: str = '', role: str = '', country: str = '') -> tuple[int, str]:
    key = build_version_key(asset_type, full_name, role, country)
    versions = [int(asset.get('version', 0) or 0) for asset in existing_assets if asset.get('version_key') == key]
    version = (max(versions) if versions else 0) + 1
    return version, key


def enrich_versions(assets: list[dict]) -> list[dict]:
    grouped = {}
    for asset in assets:
        grouped.setdefault(asset.get('version_key', ''), []).append(asset)
    for bucket in grouped.values():
        bucket.sort(key=lambda item: item.get('created_at', ''))
        latest_id = bucket[-1].get('id') if bucket else None
        total = len(bucket)
        for asset in bucket:
            actions = list(asset.get('available_actions', []))
            if total > 1 and 'compare' not in actions:
                actions.append('compare')
            if asset.get('id') != latest_id and 'restore' not in actions:
                actions.append('restore')
            asset['available_actions'] = actions
            asset['version_count'] = total
    return assets
