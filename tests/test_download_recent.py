import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python" / "ingestion"))
import download_recent as download


class Response(io.BytesIO):
    def __init__(self, body, url, **headers):
        super().__init__(body)
        self.url = url
        self.headers = headers


def archive(text):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as file:
        file.writestr("records.csv", text)
    return stream.getvalue()


class DownloadTests(unittest.TestCase):
    def test_revalidation_preserves_original_on_error_and_new_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "http://www.dgis.salud.gob.mx/records_2024.zip"
            page = f'<a href="{url}">Registros</a>'.encode()
            first = archive("edad\n40\n")
            second = archive("edad\n41\n")
            received = iter([first, None, b"<html>Error</html>", second])

            def fetch(request, timeout):
                if isinstance(request, str):
                    return Response(page, request)
                data = next(received)
                if data is None:
                    self.assertEqual(request.get_header("If-none-match"), '"v1"')
                    raise HTTPError(url, 304, "Not modified", {}, None)
                etag = '"v1"' if data == first else '"v2"'
                ctype = "text/html" if data.startswith(b"<html>") else "application/zip"
                return Response(data, url, ETag=etag, **{"Content-Type": ctype})

            with patch.object(download, "ROOT", root), patch.object(download, "PAGES", {"defunciones": "test.html"}), patch.object(download.urllib.request, "urlopen", fetch):
                self.assertTrue(download.run())
                self.assertTrue(download.run())
                self.assertFalse(download.run())
                self.assertEqual([p.read_bytes() for p in root.rglob("*.zip")], [first])
                self.assertTrue(download.run())
                self.assertCountEqual([p.read_bytes() for p in root.rglob("*.zip")], [first, second])
                self.assertFalse(list(root.rglob("*.part")))
