import simplejson, urllib
import re

ADR="Villeurbanne69100RhoneFrance"
LIMIT_KM=1000
LIMIT_TIME=60

LIST_MOT_TITLE=['velo', 'vtt']


def checkWord(chaine, mot):
	p = re.compile(str(mot), re.IGNORECASE)
	if p.match(chaine):
		return True
	return False
	
def returnMatching(pattern, chaine):
	t=re.search(pattern, chaine)

	if t:
		return t.group
	return False
	
	
def checkTitle(title):	
	for mot in LIST_MOT_TITLE:
		if checkWord(title, mot):
			return True
	
	return False

def computeDistanceTime(adr2):
	url="http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(ADR), str(adr2))
	result=simplejson.load(urllib.urlopen(url))
	if result['rows'][0]['elements'][0]['status']!='NOT_FOUND':
		time= result['rows'][0]['elements'][0]['duration']['value']/60.0 # en min
		dist= result['rows'][0]['elements'][0]['distance']['value']/1000.0 # en km
		
		print time, "minutes", dist,"km"
		
		if time <LIMIT_TIME and dist < LIMIT_KM:
			return True
	
	return False


if __name__ == '__main__':
	cp1=69100
	cp2=38200
	ville1='Villeurbanne'
	ville2='Jardin'
	
	time, dist = computeDistanceTime(str(cp1)+ville1+"France", str(cp2)+ville2+"France")
	print time, "minutes", dist,"km"
