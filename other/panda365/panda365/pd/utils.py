

def get_by_prefix(data, prefix, remove_prefix=True):
    """
    get values from a dict by key prefix. E.g.:

        data = {
            'aws_access_key': '123',
            'aws_access_secret': '234',
            'secret': '456'
        }
        assert get_by_prefix(data, 'aws_') == {
            'access_key': '123',
            'access_secret': '234'
        }

    """
    ret = {}
    l = len(prefix)
    for k, v in data.items():
        if k.startswith(prefix):
            k = k[l:] if remove_prefix else k
            ret[k] = v
    return ret
