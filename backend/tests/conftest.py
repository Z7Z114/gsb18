"""测试夹具：把后端跑在临时目录 + 临时 SQLite 上，全程离线。"""
import os
import sys
import tempfile
from pathlib import Path

# 仓库根目录（backend/ 的上一级），让 `import backend.*` 在 backend/ 下也能用
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_TMP = Path(tempfile.mkdtemp(prefix="temple-tests-"))

# settings / engine 都在 import 时构造，所以必须先落环境变量再 import backend
os.environ["DATABASE_URL"] = "sqlite:///" + (_TMP / "test.db").as_posix()
os.environ["TEMP_AUDIO_DIR"] = str(_TMP / "temp_audio")
os.environ["OUTPUT_DIR"] = str(_TMP / "output")
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:9/v1"
os.environ["PYANNOTE_AUTH_TOKEN"] = ""
os.environ["SMTP_HOST"] = ""
os.environ["SMTP_USER"] = ""
os.environ["SMTP_PASSWORD"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.database import Base, engine  # noqa: E402
from backend.main import app  # noqa: E402


@pytest.fixture()
def client():
    """每个用例一个干净的库 + 一个 TestClient。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def tmp_root():
    return _TMP
