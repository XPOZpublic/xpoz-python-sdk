from __future__ import annotations

import json
import socket
import warnings
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from xpoz._update_check import XpozUpdateWarning, check_for_update


def _make_pypi_response(version: str) -> MagicMock:
    data = json.dumps({"info": {"version": version}}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = data
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestCheckForUpdate:
    @patch("xpoz._update_check.__version__", "0.2.0")
    @patch("xpoz._update_check.urlopen")
    def test_warns_when_outdated(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _make_pypi_response("0.3.0")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_for_update()

        assert len(w) == 1
        assert issubclass(w[0].category, XpozUpdateWarning)
        assert "v0.3.0" in str(w[0].message)
        assert "pip install --upgrade xpoz" in str(w[0].message)

    @patch("xpoz._update_check.__version__", "0.3.0")
    @patch("xpoz._update_check.urlopen")
    def test_no_warning_when_current(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _make_pypi_response("0.3.0")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_for_update()

        assert len(w) == 0

    @patch("xpoz._update_check.urlopen")
    def test_no_exception_on_network_error(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = URLError("DNS failure")
        check_for_update()

    @patch("xpoz._update_check.urlopen")
    def test_no_exception_on_timeout(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = socket.timeout("timed out")
        check_for_update()

    @patch("xpoz._update_check.urlopen")
    def test_no_exception_on_malformed_json(self, mock_urlopen: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        check_for_update()

    @patch("xpoz._update_check.check_for_update")
    @patch("xpoz._client.SyncTransport")
    def test_check_update_false_skips_thread(
        self, mock_transport_cls: MagicMock, mock_check: MagicMock
    ) -> None:
        mock_transport = MagicMock()
        mock_transport_cls.return_value = mock_transport

        from xpoz._client import XpozClient

        client = XpozClient(api_key="test-key", check_update=False)
        mock_check.assert_not_called()
        client.close()
