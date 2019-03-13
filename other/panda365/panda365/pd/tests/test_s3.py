import pytest
from pd.s3 import S3Storage


@pytest.mark.parametrize('bucket,expect_calling_format', [
    ['images.example.org', True],
    ['images', False]
])
def test_connect_calling_format(bucket, expect_calling_format, mock_boto_s3):
    s3 = S3Storage(bucket, 'ap-southeast-1', 'key', 'secret')
    s3.bucket  # noqa: implicitly connect
    kwargs = mock_boto_s3.connect_to_region.call_args[1]
    assert ('calling_format' in kwargs) == expect_calling_format
