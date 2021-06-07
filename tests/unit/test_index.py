import pytest

from s3pypi.index import Filename, Index


@pytest.fixture(
    scope="function",
    params=[
        (
            "s3pypi",
            [
                f"s3pypi-{version}{suffix}"
                for version in (
                    "0",
                    "0!0",
                    "0+local",
                    "0.0",
                    "0.1.1",
                    "0.1.2",
                    "0.dev0",
                    "0.post0",
                    "0a0",
                    "0rc0",
                )
                for suffix in (
                    ".tar.gz",
                    "-py2-none-any.whl",
                )
            ],
            ["1234" * 16 if i % 3 == 0 else "" for i in range(0, 20)],
        )
    ],
)
def index_html(request, data_dir):
    index_name, names, hashes = request.param
    filenames = {
        name: Filename(name, "sha256", hash) if hash else Filename(name)
        for name, hash in zip(names, hashes)
    }
    with open(data_dir / "index" / f"{index_name}.html") as f:
        html = f.read().strip()
        yield html, filenames


def test_parse_index(index_html):
    html, expected_filenames = index_html
    index = Index.parse(html)
    assert index.filenames == expected_filenames


def test_render_index(index_html):
    expected_html, filenames = index_html
    html = Index(filenames).to_html()
    assert html == expected_html


@pytest.mark.parametrize(
    "filename,expected",
    [
        (Filename("3pypi-0.post0-py2-none-any.whl"), "3pypi-0.post0-py2-none-any.whl"),
        (
            Filename("3pypi-0.post0.tar.gz", "sha256", "12345"),
            "3pypi-0.post0.tar.gz#sha256=12345",
        ),
        (
            Filename("3pypi-0+local.tar.gz", "md5", "abcdef"),
            "3pypi-0%2Blocal.tar.gz#md5=abcdef",
        ),
    ],
)
def test_filename_url(filename, expected):
    assert filename.url_path == expected
