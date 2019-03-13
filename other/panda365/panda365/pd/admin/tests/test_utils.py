from PIL import Image
from pd.admin.utils import create_cover_for_gif


def test_gif_cover(gif_path):
    with open(gif_path, mode='rb') as gif:
        fp = create_cover_for_gif(gif)
        cover = Image.open(fp)
        assert cover.format == 'JPEG'
