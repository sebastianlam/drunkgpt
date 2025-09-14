import json
from logging_utils import session_log


def test_session_log_appends_entry(tmp_path):
    log_file = tmp_path / "log.json"
    log_file.write_text(json.dumps({"chats": []}))
    context = [{"role": "system", "content": "hi"}]
    session_log(str(log_file), context, "start", "gpt-4")
    data = json.loads(log_file.read_text())
    assert len(data["chats"]) == 1
    entry = data["chats"][0]
    assert entry["start"] == "start"
    assert entry["model"] == "gpt-4"
    assert entry["content"] == context
    assert "end" in entry
