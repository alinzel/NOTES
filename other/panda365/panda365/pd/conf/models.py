from pd.sqla import db


class Conf(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.Text, nullable=False, unique=True,
        doc='客户端名称. 例如`ios`, `android`',
    )
    min_version = db.Column(
        db.Integer, nullable=False,
        doc='最小客户端版本号。当客户端版本小于此版本时，应**强制**更新'
    )
    latest_version = db.Column(
        db.Integer, nullable=False,
        doc='最新版客户端的版本号。当客户端版本小于此版本但大于最小版本'
            '时，应**推荐**更新'
    )
    description = db.Column(db.Text, doc='最新版本的说明/简介')
