import textwrap
from pathlib import Path

import log_study


def analyse(tmp_path: Path, code: str):
    f = tmp_path / "m.py"
    f.write_text(textwrap.dedent(code))
    return log_study.analyse_file(f)


def test_counts_levels_and_loc(tmp_path):
    loc, levels, handlers = analyse(tmp_path, """
        import logging
        logger = logging.getLogger(__name__)
        # a comment
        logger.info("x")
        logger.error("y")
        logging.warning("z")
    """)
    assert levels["info"] == 1 and levels["error"] == 1 and levels["warning"] == 1
    assert loc == 5  # blank and comment lines are not counted


def test_ignores_non_logger_receivers(tmp_path):
    _, levels, _ = analyse(tmp_path, "x = 1\nself.info('not a log call')\nresult.error('nope')\n")
    assert sum(levels.values()) == 0


def test_handler_classification(tmp_path):
    _, _, handlers = analyse(tmp_path, """
        import logging
        log = logging.getLogger()
        try:
            a()
        except ValueError:
            log.exception("bad")
        try:
            a()
        except KeyError:
            raise
        try:
            a()
        except OSError:
            pass
    """)
    assert handlers == [(True, False, False), (False, True, False), (False, False, True)]


def test_syntax_error_returns_none(tmp_path):
    assert analyse(tmp_path, "def broken(:\n") is None
