import json


class Video:
	"""docstring for Video"""
	def __init__(self, url='', title='', viewCount='', thumbnail='', publishedTime='', duration=''):
		self.url = url
		self.title = title
		self.viewCount = viewCount
		self.thumbnail = thumbnail
		self.publishedTime = publishedTime
		self.duration = duration

	def __repr__(self):
		return f'{self.title} {self.duration} {self.url}'

	def fromJson(js):
		if js['type'] == 'video':
			return Video(
				url=js['link'], 
				title=js['title'], 
				duration= js['duration'], 
				viewCount=js['viewCount'], 
				thumbnail=js['thumbnails'][0]['url'], 
				publishedTime = js['publishedTime'],
				)
	# def toJ