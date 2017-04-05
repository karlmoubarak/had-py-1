import os
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from jinja2 import Environment, FileSystemLoader


class had(object):

	def __init__(self):
		template_path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jinja_env = Environment(loader=FileSystemLoader(template_path),
																 autoescape=True)
		self.url_map = Map([
			Rule('/', endpoint='home')
		])
		
	def on_home(self, request):
		
		#fetch content
		url_content = "https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=parse&page=Hackers_%26_Designers&format=json&formatversion=2&disableeditsection=true"
		response_content = requests.get(url_content)
		wikidata = response_content.json()

		wikititle = wikidata['parse']['title']
		wikibodytext = wikidata['parse']['text']
	
		#	
		#url_event_list = "https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=query&generator=categorymembers&gcmtitle=Category:Events&gcmsort=timestamp&gcmdir=desc&prop=info&inprop=url&format=json&formatversion=2
		url_event_list = "https://wiki.hackersanddesigners.nl/mediawiki/api.php?action=query&list=categorymembers&cmtitle=Category:Events&cmsort=timestamp&cmdir=desc&format=json&formatversion=2"
		response_event_list = requests.get(url_event_list)
		wikidata_event_list = response_event_list.json()

		# fix rel-link to be abs-ones
		base_url = 'http://wikidev.hackersanddesigners.nl'
		soup = BeautifulSoup(wikibodytext, 'html.parser')

		for a in soup.find_all('a', href=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
			rel_link = a.get('href')
			out_link = urljoin(base_url, rel_link)
			a['href'] = out_link

		for img in soup.find_all('img', src=re.compile(r'^(?!(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//))')):
			rel_link = img.get('src')
			out_link = urljoin(base_url, rel_link)
			img['src'] = out_link

		wikibodytext = soup

		#build template
		return self.render_template('index.html', 
			title=wikititle, 
			bodytext=wikibodytext,
			event_title=wikidata_event_list
		)

	def error_404(self):
		response = self.render_template('404.html')
		response.status_code = 404
		return response

	def render_template(self, template_name, **context):
		t = self.jinja_env.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	def dispatch_request(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try:
			endpoint, values = adapter.match()
			return getattr(self, 'on_' + endpoint)(request, **values)
		except NotFound as e:
			return self.error_404()
		except HTTPException as e:
			return e

	def wsgi_app(self, environ, start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)

	
def create_app(with_assets=True):
	app = had()
	if with_assets:
		app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
			'/assets': os.path.join(os.path.dirname(__file__), 'assets')
		})
	return app
	
if __name__ == '__main__':
	from werkzeug.serving import run_simple
	app = create_app()
	run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
