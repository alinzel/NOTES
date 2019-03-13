from blinker import signal


fb_post_add = signal('fb_post_add')
fb_post_edited = signal('fb_post_edited')
fb_post_remove = signal('fb_post_remove')
fb_comment_add = signal('fb_comment_add')
fb_comment_edited = signal('fb_comment_edited')
fb_comment_remove = signal('fb_comment_remove')
fb_like_add = signal('fb_like_add')
fb_like_remove = signal('fb_like_remove')
