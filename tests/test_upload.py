import io
import pytest
from apps.api.app.core.errors import FileSizeExceededError, UnsupportedMediaTypeError, InvalidFileError
from apps.api.app.services.upload_service import upload_service


def test_upload_valid_jpeg(sample_valid_jpeg):
    mime, sha256_val, phash_val, norm_name, preview = upload_service.validate_and_process(
        file_bytes=sample_valid_jpeg,
        filename="test_photo.jpg",
        content_type="image/jpeg"
    )
    assert mime == "image/jpeg"
    assert len(sha256_val) == 64
    assert phash_val is not None
    assert len(preview) > 0


def test_upload_valid_png(sample_valid_png):
    mime, sha256_val, phash_val, norm_name, preview = upload_service.validate_and_process(
        file_bytes=sample_valid_png,
        filename="test_graphic.png",
        content_type="image/png"
    )
    assert mime == "image/png"
    assert len(sha256_val) == 64


def test_upload_valid_webp(sample_valid_webp):
    mime, sha256_val, phash_val, norm_name, preview = upload_service.validate_and_process(
        file_bytes=sample_valid_webp,
        filename="test_image.webp",
        content_type="image/webp"
    )
    assert mime == "image/webp"
    assert len(sha256_val) == 64


def test_upload_file_size_exceeded():
    large_payload = b"\xFF\xD8\xFF" + b"\x00" * (21 * 1024 * 1024)
    with pytest.raises(FileSizeExceededError):
        upload_service.validate_and_process(
            file_bytes=large_payload,
            filename="too_large.jpg",
            content_type="image/jpeg"
        )


def test_upload_fake_extension_non_image():
    fake_payload = b"Hello world this is not an image file at all"
    with pytest.raises(UnsupportedMediaTypeError):
        upload_service.validate_and_process(
            file_bytes=fake_payload,
            filename="fake_image.jpg",
            content_type="image/jpeg"
        )


def test_upload_corrupted_header():
    corrupted = b"\xFF\xD8\xFF" + b"randomcorruptedbytes12345"
    with pytest.raises(InvalidFileError):
        upload_service.validate_and_process(
            file_bytes=corrupted,
            filename="broken.jpg",
            content_type="image/jpeg"
        )


def test_api_upload_endpoint(client, sample_valid_jpeg):
    files = {"file": ("test.jpg", sample_valid_jpeg, "image/jpeg")}
    data = {"claim": "Photo prise aujourd'hui à Ouagadougou"}
    response = client.post("/api/v1/analyses", files=files, data=data)
    assert response.status_code == 202
    json_data = response.json()
    assert "analysis_id" in json_data
    assert "public_id" in json_data
    assert json_data["status"] == "pending"
    assert json_data["access_token"] is not None # Anonymous token returned
