import aioboto3
from app.core.config import settings
from botocore.config import Config


class AsyncMinioClient:
    def __init__(self):
        self.session = aioboto3.Session()
        self.client_params = dict(
            service_name="s3",
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )

    async def upload_bytes(self, bucket: str, object_name: str, data: bytes, content_type: str):
        if not data:
            raise ValueError("Cannot upload empty file")

        async with self.session.client(**self.client_params) as s3:
            await s3.put_object(
                Bucket=bucket,
                Key=object_name,
                Body=data,
                ContentType=content_type,
            )
        return f"{bucket}/{object_name}"

    async def download_bytes(self, bucket: str, object_name: str) -> bytes | None:
        async with self.session.client(**self.client_params) as s3:
            try:
                response = await s3.get_object(Bucket=bucket, Key=object_name)
                return await response["Body"].read()
            except Exception as e:
                print(f"MinIO download error: {e}")
                return None

    async def delete_object(self, bucket: str, object_name: str) -> bool:
        async with self.session.client(**self.client_params) as s3:
            try:
                await s3.delete_object(Bucket=bucket, Key=object_name)
                return True
            except Exception as e:
                print(f"MinIO delete error: {e}")
                return False

    async def generate_presigned_url(self, bucket: str, object_name: str, expires=3600) -> str | None:
        async with self.session.client(**self.client_params) as s3:
            try:
                return await s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": bucket, "Key": object_name},
                    ExpiresIn=expires,
                )
            except Exception as e:
                print(f"Error generating presigned URL: {e}")
                return None

    async def ensure_bucket_exists(self, bucket: str):
        async with self.session.client(**self.client_params) as s3:
            try:
                await s3.head_bucket(Bucket=bucket)
            except Exception:
                await s3.create_bucket(Bucket=bucket)

# -------------- THIS LINE IS REQUIRED --------------
async_minio = AsyncMinioClient()