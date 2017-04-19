from django.template import Library

from video.models import YoutubeVideo

register = Library()

@register.inclusion_tag('video/youtube.html')
def embed_youtube(video_id, width=640, height=480):
    if video_id.startswith('http'):
        video_id = YoutubeVideo.video_id_from_url(video_id)
    return {'video_id': video_id, 'width': width, 'height': height}