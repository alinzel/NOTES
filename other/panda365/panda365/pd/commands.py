import click
from furl import furl
from flask import current_app
from pd.auth.jwt import create_token as create_jwt_token
from pd.facebook.models import User, PostPhoto
from pd.facebook.signal_handlers.utils import sync_fb_static_file
from pd.guest.models import GuestUsers
from pd.sqla import db
from pd.bot.commands import (
    create_bot, rename_images, create_bot_commands, update_game_left_share)


def urls():
    """
    show all urls
    """
    rules = [rule for rule in current_app.url_map.iter_rules()]
    rules.sort(key=lambda rule: rule.rule)
    print('\n'.join(repr(rule) for rule in rules))
    return rules


@click.argument('user_id', type=click.INT)
def create_token(user_id):
    """
    create jwt token for user
    """
    u = User.query.get(user_id)
    if not u:
        click.get_current_context().fail(
            'user {} does not exist'.format(user_id))
    token = create_jwt_token(u)
    click.echo(token)
    return token


def sync_photos():
    photos = PostPhoto.query.filter(
        PostPhoto.url.op('!~')('\/(\w+)_(\d+)_(\d+)\.(\w+)$')
    ).all()
    total = len(photos)

    todo = []

    for i, photo in enumerate(photos):
        url = photo.url
        if url.startswith('//'):
            # old photos do not have protocol
            url = 'http:' + url
        # remove possible dimension in query args
        f_url = furl(url)
        f_url.args.pop('_w', None)
        f_url.args.pop('_h', None)
        url = str(f_url)

        try:
            current_app.logger.info(
                'photo[%d] - syncing : %s', photo.id, photo.url)
            url = sync_fb_static_file(url)
        except Exception as e:
            current_app.logger.error(
                'photo[%d]: error when syncing %s: %s',
                photo.id, photo.url, e)
            todo.append(photo.id)
        else:
            if url:
                photo.url = url
                db.session.commit()
                current_app.logger.info('photo[%d]: sync success', photo.id)
            else:
                current_app.logger.info(
                    'photo[%d]: fail to get url for %s', photo.id, photo.url)
                todo.append(photo.id)
        current_app.logger.info(
            'progress: %.1f%%(%d/%d)', 100 * (i + 1) / total, i + 1, total)

    current_app.logger.info(
        'sync done. The following may need manual processing: %s', todo)
    return total - len(todo)


@click.argument('account')
@click.argument('pw')
def create_guest_account(account, pw):
    user = GuestUsers(account=account, pw=pw)
    db.session.add(user)
    db.session.commit()


def init_app(app):
    app.cli.command()(urls)
    app.cli.command()(create_token)
    app.cli.command()(create_bot)
    app.cli.command()(rename_images)
    app.cli.command()(create_bot_commands)
    app.cli.command()(update_game_left_share)
    app.cli.command()(create_guest_account)
