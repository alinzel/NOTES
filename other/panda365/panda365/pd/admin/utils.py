from tempfile import TemporaryFile
from PIL import Image, ImageSequence


def create_cover_for_gif(gif_fp):
    """
    create the cover image for the given gif. The first frame is taken and
    is coverted into jpeg. The result is hold in a tmpfile.

    :gif_fp: a file-like object to the gif
    :returns: a file-like object to the jpeg cover image
    """
    gif = Image.open(gif_fp)
    cover = ImageSequence.Iterator(gif)[0]
    fp = TemporaryFile()
    cover.convert('RGB').save(fp, format='jpeg')
    return fp
