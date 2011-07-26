import urllib,urllib2,re,os,cookielib
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP

addon = xbmcaddon.Addon('plugin.video.glwiz')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))

__settings__ = xbmcaddon.Addon(id='plugin.video.glwiz')
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )

if __settings__.getSetting('paid_account') == "true":
        if (__settings__.getSetting('username') == "") or (__settings__.getSetting('password') == ""):
                xbmc.executebuiltin("XBMC.Notification('GLWiZ','Enter username and password.',30000,"+icon+")")
                __settings__.openSettings()

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

def login():
	resp = opener.open('http://www.glwiz.com/')
	html_data = resp.read();
	soup = BeautifulSoup(html_data)
	eventVal = soup.find('input',id='__EVENTVALIDATION',type='hidden')
	viewState = soup.find('input',id='__VIEWSTATE',type='hidden')
	loginURL = 'http://www.glwiz.com/homepage.aspx?__EVENTARGUMENT=&__EVENTTARGET=&__EVENTVALIDATION=%s&__VIEWSTATE=%s&pageHeader%%24ScriptManager1=pageHeader%%24UpdatePanel1%%7CpageHeader%%24buttonLogin&pageHeader%%24buttonLogin=%%20&pageHeader%%24txtPassword=%s&pageHeader%%24txtUsername=%s' % (urllib.quote(eventVal['value']), urllib.quote(viewState['value']), urllib.quote(__settings__.getSetting('password')), urllib.quote(__settings__.getSetting('username')))
	opener.open(loginURL)
	resp = opener.open('http://www.glwiz.com/ajax.aspx?channel=tvlist&type=reg&genre=1')
	html_data = resp.read();
	return html_data != 'NoAccess'	

def getCategories():
	if __settings__.getSetting('paid_account') == "true":
		while not login():
        	        xbmc.executebuiltin("XBMC.Notification('GLWiZ','INVALID username and/or password.',30000,"+icon+")")
	                __settings__.openSettings()
		try:
			resp = opener.open('http://www.glwiz.com/ajax.aspx?channel=tvlist&type=reg&genre=1')
			html_data = resp.read();
			soup = BeautifulSoup(html_data)
			categories = soup.find('ul',id='categoryContainer')
			pattern = re.compile('tvChannelsStart\(\'(.*?)\'\);')
			for li in categories:
				name = li.contents[0].strip()
				dirurl = pattern.search(li['onclick']).groups()[0]
				if dirurl == '-1':
					pass
				dirurl = 'http://www.glwiz.com/ajax.aspx?channel=tv&genre=' + dirurl
				addDir(name,dirurl,1)			
		except:
			return
	else:
		try:
			resp = opener.open('http://www.glwiz.com/ajax.aspx?channel=tv&type=free&genre=1')
			html_data = resp.read();
			soup = BeautifulSoup(html_data)
			categories = soup.find('ul',id='listContainerTopMenu')
			pattern = re.compile('\&genre=(.*?)\&')
			for li in categories:
				name = li.contents[0].strip()
				dirurl = 'http://www.glwiz.com/ajax.aspx?channel=tv&genre=' + pattern.search(li['onclick']).groups()[0]
				addDir(name,dirurl,1)
		except:
			return
                        
def getChannels(url):
	if __settings__.getSetting('paid_account') == "true":
		while not login():
        	        xbmc.executebuiltin("XBMC.Notification('GLWiZ','INVALID username and/or password.',30000,"+icon+")")
	                __settings__.openSettings()
		url += '&type=reg'
	else:
		url += '&type=free'

	resp = opener.open(url)
	inner_data = resp.read();
	inner_soup = BeautifulSoup(inner_data)
	container = inner_soup.find('div',id='listContainerScroll')

	thumbnail = "DefaultVideo.png"
	pattern = pattern = re.compile("\makeHttpRequest\(\'(.*?)\&\',")

	for span in container:
		try:
			itemurl = 'http://www.glwiz.com/' + pattern.search(span['onclick']).groups()[0]
			if __settings__.getSetting('show_thumbnail') == "true":
				thumbnail = span.contents[0]['src']
			name = span.contents[1].strip()	
			response = opener.open(itemurl)
			link=response.read()
			itemurl =link.replace('http://','mms://')
	                addLink(itemurl,name,thumbnail)
		except:
			pass

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param


def addDir(name,url,mode):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(url,name,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

            
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

if mode==None:
        print ""
        getCategories()

elif mode==1:
        print ""+url
        getChannels(url)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))