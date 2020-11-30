
def ValidatePhotoLink(url: str) -> bool:
    return (url.startswith('http://') or url.startswith('https://')) and \
           (url.endswith('.jpg') or url.endswith('.png'))
