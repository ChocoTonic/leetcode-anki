import asyncio
import sqlite3
import zipfile
from pathlib import Path
from unittest import mock

from generate import generate
from test.helpers.test_leetcode import QUESTION_DETAIL


def test_generate_writes_anki_package(tmp_path: Path) -> None:
    output = tmp_path / "sample.apkg"
    with mock.patch(
        "leetcode_anki.helpers.leetcode.LeetcodeData._get_problems_data",
        return_value=[QUESTION_DETAIL],
    ):
        asyncio.run(generate(0, 1, 2, "", str(output)))

    with zipfile.ZipFile(output) as package:
        database = tmp_path / "collection.anki2"
        database.write_bytes(package.read("collection.anki2"))
        assert "media" in package.namelist()
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM notes").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM cards").fetchone() == (1,)
        fields = connection.execute("SELECT flds FROM notes").fetchone()[0]
        assert QUESTION_DETAIL.title in fields
        assert QUESTION_DETAIL.content in fields
