
from flask import Blueprint, \
    render_template, flash, request, \
    url_for, jsonify, session
from werkzeug.utils import redirect

from pd.facebook.models import Comment, User
from pd.groupon.models import Product
from pd.guest.forms import LoginForm
from pd.guest.models import GuestUsers
from pd.sqla import db

reply = Blueprint(
    'comments_reply', __name__,
    template_folder='templates',
)


@reply.route('/comments_reply/login.html', methods=['GET', 'POST'])
def reply_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = GuestUsers.query.filter_by(account=form.account.data).first()
        if user and user.verify_password(form.password.data):
            session['account'] = user.account
            session['password'] = form.password.data
            return redirect(url_for('.comments_list'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@reply.route('/comments_reply/comments.html')
def comments_list():
    account = session.get('account')
    if account:
        user = GuestUsers.query.filter_by(account=account).first()
        if user and user.verify_password(session.get('password')):

            # product_all = Product.query.order_by(Product.created_at.desc())
            post_comments = Comment.query. \
                join(Product, Comment.parent_id == Product.id). \
                filter(Comment.parent_type == 'Product'). \
                order_by(Comment.created_at.desc())

            page = request.args.get('page', 1, type=int)
            pagination = post_comments.paginate(page, per_page=10)
            comments = pagination.items
            prev = None
            if pagination.has_prev:
                prev = url_for('comments_reply.comments_list',
                               page=page - 1, _external=True)

            next = None
            if pagination.has_next:
                next = url_for('comments_reply.comments_list',
                               page=page + 1, _external=True)
            return render_template('reply.html',
                                   comments=comments,
                                   prev=prev,
                                   next=next
                                   )
    return redirect(url_for('.reply_login'))


@reply.route('/comments_reply/reply/', methods=['POST'])
def replay_comment():
    reply_comment_body = '''
                     <div id="messages">

                <div class="head">
                    <img class="header" src="{reply_user_icon_url}">
                    <div class="name"> {reply_user_name}</div>
                </div>

                <div class="message">{reply_message}</div>
                <div class="time">
                    <div style="float: left">{reply_created_at}</div>
                </div>
            </div>
                    '''
    comment_id = request.form.get('id')
    message = request.form.get('message', '')
    comment = Comment.query.filter(Comment.id == int(comment_id)).first()
    user = User.query.filter(User.id == 7068).first()
    if not user:
        user = User.query.filter().first()

    replay_comment = Comment(
        message=message,
        user=user,
        parent=comment,
        parent_id=comment.id,
        parent_type='Comment',
        photo_url=''
    )
    db.session.add(replay_comment)
    db.session.commit()
    flash('Your comment has been published')
    reply_comment_body = reply_comment_body.format(
        reply_id=replay_comment.id,
        reply_user_icon_url=getattr(user, 'icon_url', ''),
        reply_user_name=replay_comment.user.name,
        reply_created_at=replay_comment.created_at.format(
            'YYYY-MM-DD HH:mm ZZ'),
        reply_message=replay_comment.message
    )
    data = {
        'html': reply_comment_body,
    }

    return jsonify(data)
