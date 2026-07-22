from html import escape

def content_info(m):
    if m.text is not None:return 'text',None,m.text
    if m.photo:return 'photo',m.photo[-1].file_id,m.caption
    if m.video:return 'video',m.video.file_id,m.caption
    if m.document:return 'document',m.document.file_id,m.caption
    if m.voice:return 'voice',m.voice.file_id,m.caption
    if m.sticker:return 'sticker',m.sticker.file_id,None
    return m.content_type,None,m.caption
def profile(uid,name): return f'<a href="tg://user?id={uid}">{escape(name)}</a>'
