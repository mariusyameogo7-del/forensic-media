import os
import io
from pathlib import Path
from typing import Optional, BinaryIO, Union
from apps.api.app.core.config import settings


class StorageService:
    """
    Private storage service interacting with Supabase Storage (or local storage in dev/test).
    All buckets are strictly private.
    """

    def __init__(self):
        self.local_storage_path = Path("temp_uploads")
        self.local_storage_path.mkdir(exist_ok=True, parents=True)
        self._supabase_client = None

    def _get_supabase(self):
        if self._supabase_client is None and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY != "dummy-service-role-key":
            try:
                from supabase import create_client
                self._supabase_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
            except Exception:
                self._supabase_client = None
        return self._supabase_client

    def upload_file(
        self,
        bucket_name: str,
        storage_path: str,
        data: Union[bytes, BinaryIO],
        content_type: str
    ) -> str:
        """
        Uploads an object to private storage and returns the storage reference path.
        """
        client = self._get_supabase()
        binary_data = data if isinstance(data, bytes) else data.read()

        if client is not None:
            try:
                client.storage.from_(bucket_name).upload(
                    path=storage_path,
                    file=binary_data,
                    file_options={"content-type": content_type, "upsert": "true"}
                )
                return storage_path
            except Exception:
                pass

        # Fallback to local storage (for dev without Supabase keys or unit testing)
        target_dir = self.local_storage_path / bucket_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / storage_path.replace("/", "_")
        with open(target_file, "wb") as f:
            f.write(binary_data)
        return storage_path

    def download_file(self, bucket_name: str, storage_path: str) -> bytes:
        """Downloads an object from private storage."""
        client = self._get_supabase()
        if client is not None:
            try:
                res = client.storage.from_(bucket_name).download(storage_path)
                return res
            except Exception:
                pass

        target_file = self.local_storage_path / bucket_name / storage_path.replace("/", "_")
        if target_file.exists():
            with open(target_file, "rb") as f:
                return f.read()
        raise FileNotFoundError(f"File not found in storage: {bucket_name}/{storage_path}")

    def create_signed_url(self, bucket_name: str, storage_path: str, expires_in_seconds: int = 3600) -> str:
        """Generates a temporary signed URL for private access."""
        client = self._get_supabase()
        if client is not None:
            try:
                res = client.storage.from_(bucket_name).create_signed_url(storage_path, expires_in_seconds)
                return res.get("signedURL") or res.get("signedUrl", "")
            except Exception:
                pass
        return f"/api/v1/storage/{bucket_name}/{storage_path}"

    def delete_file(self, bucket_name: str, storage_path: str) -> bool:
        """Deletes an object from private storage."""
        client = self._get_supabase()
        if client is not None:
            try:
                client.storage.from_(bucket_name).remove([storage_path])
            except Exception:
                pass

        target_file = self.local_storage_path / bucket_name / storage_path.replace("/", "_")
        if target_file.exists():
            try:
                target_file.unlink()
                return True
            except Exception:
                return False
        return True


storage_service = StorageService()
