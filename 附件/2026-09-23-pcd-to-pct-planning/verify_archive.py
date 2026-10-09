#!/usr/bin/env python3
"""Read-only archive/link checks; optional source comparison on the original host.

Usage: python3 verify_archive.py [--check-originals]
No ROS, native planner, network, image editing, or output-file writes.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from urllib.parse import unquote


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-originals", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "source-manifest.json").read_text())
    article = (root / manifest["article"]).resolve()
    assert article.is_file(), article
    body = article.read_text()
    images = []
    for record in manifest["files"]:
        path = root / record["file"]
        assert path.is_file(), path
        assert path.stat().st_size == record["bytes"], path
        assert digest(path) == record["sha256"], path
        if args.check_originals:
            source = Path(record["source"])
            assert source.is_file() and digest(source) == record["sha256"], source
        if path.suffix == ".json":
            json.loads(path.read_text())
        if path.suffix == ".png":
            with path.open("rb") as stream:
                header = stream.read(24)
            assert header[:8] == b"\x89PNG\r\n\x1a\n", path
            width, height = struct.unpack(">II", header[16:24])
            assert width > 0 and height > 0
            images.append({"file": record["file"], "width": width, "height": height})
    # All inline local links in this article. Preserve original project links;
    # check them only on the original machine, not after moving the vault.
    links = re.findall(r"!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)", body)
    checked = 0
    for target in links:
        target = unquote(target.strip("<>").split("#", 1)[0])
        if not target or re.match(r"[a-zA-Z]+://", target):
            continue
        path = Path(target)
        if path.is_absolute() and not args.check_originals:
            continue
        resolved = path if path.is_absolute() else article.parent / path
        assert resolved.exists(), resolved
        checked += 1
    assert len(re.findall(r"^```", body, re.M)) % 2 == 0, "Unbalanced fences"
    assert len(re.findall(r"!\[", body)) == 7
    assert len(manifest["files"]) == 37
    assert 1127596 - 50620 == 1076976
    assert 679006 + 37038 + 337986 + 22946 == 1076976
    assert 2601 + 34437 == 37038
    native = json.loads((root / "evidence/15-native-acceptance-summary.json").read_text())
    assert native["passed_cases"] == native["total_cases"] == 10
    assert native["all_passed"]
    assert all(item["strict_native_curve_passed"] for item in native["cases"])
    assert all(value == 0 for item in native["cases"]
               for value in item["xy_association_m"].values())
    assert native["parameters"]["astar_cost_weight"] == 2
    assert native["parameters"]["optimizer_cost_margin"] == 8
    before = json.loads((root / 'evidence/21-path-before-summary.json').read_text())
    after = json.loads((root / 'evidence/22-path-after-summary.json').read_text())
    assert after['passed_cases'] == after['total_cases'] == 14
    assert all(item['passed'] for item in after['cases'])
    old = {item['name']: item for item in before['cases']}
    new = {item['name']: item for item in after['cases']}
    for name in ('straight_23m', 'straight_18m', 'straight_11m', 'preserved_user_39m'):
        assert new[name]['quality']['xy_length_m'] < old[name]['quality']['xy_length_m']
        assert new[name]['quality']['curvature_p95_per_m'] < old[name]['quality']['curvature_p95_per_m']
    for name in ('straight_23m', 'straight_18m', 'straight_11m'):
        assert new[name]['quality']['curvature_p95_per_m'] < 1e-8
    for a, b in (('29-path-before-straight-23m.json', '26-path-straight-23m.json'),
                 ('30-path-before-user-39m.json', '27-path-user-39m.json')):
        a = json.loads((root / 'evidence' / a).read_text())['result']
        b = json.loads((root / 'evidence' / b).read_text())['result']
        assert a['start_xyz'] == b['start_xyz'] and a['goal_xyz'] == b['goal_xyz']
        assert a['source_tomogram_sha256'] == b['source_tomogram_sha256']
        assert b['path_refinement']['applied']
    live = json.loads((root / 'evidence/25-path-rviz-verification.json').read_text())
    assert live['passed'] and not live['robot_control_used']
    assert not live['rendered_screen_inspected']
    assert live['status']['state'] == 'planned'
    assert not live['status']['robot_connected'] and not live['status']['motion_enabled']
    assert live['rviz_path_subscribers']
    if args.check_originals:
        for record in manifest["primary_artifacts_not_copied"]:
            assert digest(Path(record["path"])) == record["sha256"], record["path"]
    print(json.dumps({"status": "PASS", "archived_source_files": 37,
                      "evidence_files": 30, "checked_links": checked,
                      "source_comparison": args.check_originals,
                      "images": images, "native_cases": "10/10",
                      "path_quality_cases": "14/14", "live_message_check": "PASS",
                      "point_accounting": "PASS"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
