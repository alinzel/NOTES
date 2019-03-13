import os
import sys
import uuid

from flask import current_app
import click
from pd.facebook.models import User
from pd.groupon.models import Game
from pd.sqla import db


@click.argument('image_name')
@click.argument('name')
def create_bot(image_name, name):
    user = User(
        is_bot=True,
        name=name,
        icon='https://s3-{}.amazonaws.com/{}/images/b-icons/{}'.format(
            current_app.config['S3_REGION'],
            current_app.config['S3_BUCKET'],
            image_name),
    )
    db.session.add(user)
    db.session.commit()
    print('created bot {}: {}'.format(name, user.id))
    return user


@click.argument('image_dir')
def rename_images(image_dir):   # pragma: no cover
    '''
    rename images with uuids. Only jpg, jpeg, png files are considered
    '''
    for image in os.listdir(image_dir):
        src = os.path.join(image_dir, image)
        if os.path.isfile(src):
            _, ext = os.path.splitext(image)
            if ext.lower() not in ('.jpg', '.jpeg', '.png'):
                print('the file {} does not look like an image'.format(image))
                continue
            dest = os.path.join(
                image_dir, '{}{}'.format(uuid.uuid4().hex, ext))
            print('renaming {} to {}'.format(src, dest))
            os.rename(src, dest)


@click.argument('images_dir')
def create_bot_commands(
        images_dir, names_file=None, encoding=None):    # pragma: no cover
    '''
    generate commands to run to create the bots.

    :param names_file:
        a file containing names of the bots. Each line should contain one
        name.
    :param images_dir:
        a directory containing the image files used as the icon of each user.
        The images should be uploaded to aws separately. Only their names
        are used here.
    '''
    current_app.logger.warn(
        '''
        please make sure you have uploaded the images to s3
        if you haven\'t, try the following:

            aws s3 sync --dryrun {} s3://{}/images/b-icons

        Remove `--dryrun` once you're sure about what's it doing
        '''.format(
            images_dir,
            current_app.config['S3_BUCKET'],
        ))
    images = os.listdir(images_dir)
    if names_file:
        with open(names_file, encoding=encoding) as f:
            names = f.readlines()
        total = min(len(names), len(images))
    else:
        total = len(images)
        names = None
    created = 0
    for i in range(total):
        if names:
            name = names[i].strip('\r\n').strip(',').strip()
        else:
            name = 'Carol'
        if name and not images[i].startswith('.'):
            print('flask create_bot {} "{}"'.format(images[i], name))
            created += 1
    sys.stderr.write('created {} bots, total{}'.format(created, total))


def update_game_left_share():
    games = Game.query.filter(Game.is_running).all()
    created_order = 0
    for game in games:
        orders = game.check_left_shares()
        if orders:
            created_order += orders
    db.session.commit()
    sys.stderr.write('created {} orders'.format(created_order))
