import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET = os.getenv("S3_BUCKET_NAME")


def upload_file_to_s3(local_path, s3_key):
    try:
        s3.upload_file(local_path, BUCKET, s3_key)
        print(f"✅ Uploaded to S3: {s3_key}")
        return True
    except NoCredentialsError:
        print("❌ AWS credentials not found.")
        return False
    except ClientError as e:
        print(f"❌ Upload failed: {e}")
        return False


def download_file_from_s3(s3_key, local_path):
    try:
        s3.download_file(BUCKET, s3_key, local_path)
        print(f"⬇️ Downloaded from S3: {s3_key}")
        return True
    except ClientError as e:
        print(f"❌ Download error: {e}")
        return False


def delete_user_folder_from_s3(user_id):
    try:
        prefix = f"users/{user_id}/"
        response = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
        if "Contents" in response:
            keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            result = s3.delete_objects(Bucket=BUCKET, Delete={"Objects": keys})
            deleted_count = len(result.get("Deleted", []))
            print(f"🗑️ Deleted {deleted_count} objects from S3 for user: {user_id}")
        else:
            print(f"ℹ️ No S3 files found for user: {user_id}")
    except NoCredentialsError:
        print("❌ AWS credentials not found for deletion.")
    except ClientError as e:
        print(f"❌ S3 deletion error: {e}")
