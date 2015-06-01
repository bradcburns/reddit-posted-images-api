import scrape_reddit_images

from bottle import route, template, run, static_file, request, redirect, default_app

@route('/')
def show_index():
	'''show the default index page.'''
	return static_file('index.html',root='./www/')

@route('/',method="POST")
def redirect_to_images():
	username = request.forms.get('username')
	redirect('/api/user/' + username)

@route('/api/user/<user>')
def show_image_page(user):

	StrHTML = ''
	ListImages = []

	try:
		ListComments = scrape_reddit_images.get_comments(user)
	except scrape_reddit_images.UserNotFound:
		return user + """ doesn't seem to have an account on reddit. <a href="/">go back</a>"""

	for comment in ListComments:
				DictRet = {}
				DictRet['images'] = scrape_reddit_images.GetImageURLsFromComment(comment)
				DictRet['permalink'] = ('https://www.reddit.com/comments/'
					'{submission_id}/_/{comment_id}'.format(submission_id=comment['data']['link_id'][comment['data']['link_id'].find('_')+1:],
						comment_id=comment['data']['id']))
				ListImages.append(DictRet)


	for image in ListImages:
		for subimage in image['images']:
			StrRetHTML = ('<a href="{permalink}>'
				'<img src={imgsrc}></a>'.format(
					permalink=image['permalink'],
					imgsrc=subimage))
			StrHTML += StrRetHTML



	return template('base',comments=ListImages,user=user)


if __name__ == '__main__':
	run(host='127.0.0.1',
		port=8080)
else:
	app = application = default_app()