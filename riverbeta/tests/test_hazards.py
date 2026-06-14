from riverbeta.hazards import extract_hazards


def test_extracts_english_weir():
    segments = [{"start": 10.0, "end": 12.5, "text": "There's a weir right after this bend, stay river-right."}]
    found = extract_hazards(segments)
    assert len(found) == 1
    assert found[0]["hazard_type"] == "weir"
    assert found[0]["side"] == "right"


def test_extracts_ukrainian_rapid_with_warning():
    segments = [{"start": 30.0, "end": 33.0, "text": "Обережно, далі буде поріг"}]
    found = extract_hazards(segments)
    assert len(found) == 1
    assert found[0]["hazard_type"] == "rapid"
    assert found[0]["severity"] == "high"


def test_extracts_russian_strainer_left_side():
    segments = [{"start": 5.0, "end": 7.0, "text": "Слева завал, держись правее"}]
    found = extract_hazards(segments)
    assert len(found) == 1
    assert found[0]["hazard_type"] == "strainer"
    assert found[0]["side"] == "left"


def test_no_match_returns_empty():
    segments = [{"start": 0.0, "end": 2.0, "text": "Nice and calm here, just paddling along."}]
    assert extract_hazards(segments) == []


def test_multiple_segments_multiple_hazards():
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Coming up to a rapid."},
        {"start": 5.0, "end": 7.0, "text": "Now there's a portage on the left bank."},
    ]
    found = extract_hazards(segments)
    assert [h["hazard_type"] for h in found] == ["rapid", "portage"]
    assert found[1]["side"] == "left"
