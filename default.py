import sys, os, re
import urllib, urllib2
import xbmcplugin, xbmcgui
from resources.lib.BeautifulSoup import BeautifulSoup


siteUrl		= 'http://www.cinepub.ro/'
searchUrl	= 'http://cinepub.ro/site/'
animationUrl	= 'http://cinepub.ro/site/filme/animatie/'
shortsUrl	= 'http://cinepub.ro/site/filme/scurtmetraje/'
moviesUrl	= 'http://cinepub.ro/site/filme/lungmetraje/'
documentariesUrl= 'http://cinepub.ro/site/filme/documentare/'

USER_AGENT 	= 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2062.120 Safari/537.36'
ACCEPT 		= 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

#TODO
icon = "DefaultFolder.png"#os.path.join(plugin.getPluginPath(), 'resources', 'media', 'settingsicon.png')

addonId = 'plugin.video.cinepub'

addonUrl = sys.argv[0]
addonHandle = int(sys.argv[1])

print addonUrl



def mainMenu():
	addDir('Animation',animationUrl,4,icon)
	addDir('Shorts',shortsUrl,4,icon)
	addDir('Feature',moviesUrl,4,icon)
	addDir('Documentaries',documentariesUrl,4,icon)
	addDir('Settings',siteUrl,99,icon)
	#addDir('Clear Cache',siteUrl,18)
	
	xbmcplugin.endOfDirectory(addonHandle)

def listMovies(url):
	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Please wait...')
	progress.update(1, "", "Loading list - 1%", "")

	list = []
	#TODO: caching
	movieList = BeautifulSoup(http_req("http://cinepub.ro/site/films/documentaries/")).find("div", {"class": "categoryThumbnailList"}).contents
	total = len(movieList)
	current = 0
	for movie in movieList:
		link = movie.next
		url = link['href']
		title = link['title']
		title = title[:title.find("<")]
		img = link.find("img")
		if img:
			img = img['src']
		#movieElem = {}
		#movieElem['url'] = url
		#movieElem['title'] = title
		#movieElem['thumbnail'] = img
		addDir(title,url,8,img,folder=False)
		#list.append(movieElem)

		if progress.iscanceled():
			sys.exit()

		current += 1
		percent = int((current * 100) / total)
		message = "Loading list - " + str(percent) + "%"
		progress.update(percent, "", message, "")

	progress.close()
	
	xbmcplugin.endOfDirectory(addonHandle)

def http_req(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Accept', ACCEPT)
        req.add_header('Cache-Control', 'no-transform')
        response = urllib2.urlopen(req)
        source = response.read()
        response.close()
        return source

def buildRequest(dict):
	out = {}
	for key, value in dict.iteritems():
		if isinstance(value, unicode):
			value = value.encode('utf8')
		elif isinstance(value, str):
			value.decode('utf8')
		out[key] = value
	return addonUrl + '?' + urllib.urlencode(out)

def addDir(name, url, mode, thumbnail='', folder=True):
	ok = True
	params = {'name': name, 'mode': mode, 'url': url, 'thumbnail': thumbnail}

	liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
	
	if not folder:
		liz.setProperty('isPlayable', 'true')
		liz.setProperty('resumetime', str(0))
		liz.setProperty('totaltime', str(1))
		
	liz.setInfo(type="Video", infoLabels = {"title": name})

	ok = xbmcplugin.addDirectoryItem(handle = addonHandle, url = buildRequest(params), listitem = liz, isFolder = folder)
	return ok

def getParams():
	param = {'default': 'none'}
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
			params = sys.argv[2]
			cleanedparams = params.replace('?','')
			if (params[len(params)-1] == '/'):
				params = params[0:len(params)-2]
			pairsofparams = cleanedparams.split('&')
			param = {}
			for i in range(len(pairsofparams)):
				splitparams = {}
				splitparams = pairsofparams[i].split('=')
				if (len(splitparams)) == 2:
					param[splitparams[0]] = splitparams[1]
	return param


params = getParams()

mode = int(params.get('mode', 0))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumbnail = urllib.unquote_plus(params.get('thumbnail', ''))


if mode == 0 or not url or len(url) < 1: mainMenu()
if mode == 4: listMovies(url)
