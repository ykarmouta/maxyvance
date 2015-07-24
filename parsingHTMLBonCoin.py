#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mechanize
from bs4 import BeautifulSoup
import re
import unicodedata
from unidecode import unidecode
from urlparse import urlparse
from elasticsearch import Elasticsearch
import json
from geopy.geocoders import Nominatim

#~  import shelve => sauv et lecture obj python


from DiversFonction import *


class LeBonCoin:
    """ Permet de recuperer les annonces immo
    """
    def __init__(self):
        self.liste_annonces=[]
        self.geolocator = Nominatim()
    def LirePage(self,urlPage):
        """Permet de recuperer les annonces immo d'une page
        """
        br=mechanize.Browser()
        br.set_handle_robots(False)

        ## recuperation du code html de la page
        page=br.open(urlPage)
        source=page.read()
        soup = BeautifulSoup(source)
        liste_annonces_page=soup.select("[class~=list-lbc]")[0].find_all('a')
        for annonce in liste_annonces_page:
            dico={}
            html=BeautifulSoup(str(annonce))
            try:
                lieu=html.select("[class~=placement]")[0].string.encode('utf-8').strip()
                lieu=lieu.replace('\xc3\xa2', 'a')
                lieu=lieu.replace('\xc3\xb4', 'o')
                pattern="\s*(.+)\s*\/\s*(.*)\s*"
                match=returnMatching(pattern, lieu)
                if match:
                    lieu=str(unidecode(match(1).decode('utf-8'))).replace(" ",";")+";"+str(unidecode(match(2).decode('utf-8'))).replace(" ",";")+';France'
                    geoloc = self.geolocator.geocode(lieu,geometry="geojson")
                    title=html.select("[class~=title]")[0].string.encode('utf-8').strip()
                    location= geoloc.raw['geojson']
                    title=str(unidecode(title.decode('utf-8')))
                    try:
                        prix=html.select("[class~=price]")[0].string
                        pattern="\s*([0-9 ]+).*"
                        match=returnMatching(pattern, prix)
                        prix=match(1).replace(" ","")
                        dico['prix']=int(prix)
                    except:
                        print "pas de prix"
                    date=str(html.select("[class~=date]")[0].find_all('div')[0].string)+";"+str(html.select("[class~=date]")[0].find_all('div')[1].string)
                    dico['titre']=title
                    dico['location']=location
                    dico['lien']=html.find_all('a')[0].get('href')
                    dico['date']=date
                    try:
                        dico['img']=html.select("[class~=image-and-nb]")[0].find_all('img')[0]['src']
                    except:
                        print "pas de photo"
                    json_annonce = json.dumps(dico)
                    self.liste_annonces.append(json_annonce)
            except:
                "erreur"

    def ParsePage(self,urlPage,nbPage=0):
        """Permet de recuperer les annonces immo d'une page
        """
        br=mechanize.Browser()
        br.set_handle_robots(False)
        ## recuperation du code html de la page
        page=br.open(urlPage)
        source=page.read()
        soup = BeautifulSoup(source)
        liste_annonces_page=str(soup.select("[class~=paging]")[0].find_all('li')[-1].find_all('a')[0]['href'])
        parsed = urlparse(liste_annonces_page)
        if nbPage == 0:
            nb_total_page = int(parsed.query.split('=')[1])
        else:
            nb_total_page = nbPage
        page = 1
        while page < nb_total_page :
            try:
                self.LirePage(urlPage+"?o=%s"%(page))
            except:
                print "erreur"
            page= page+1
            print "page %s"%(page)

    def VoirAnnonces(self):
        print self.liste_annonces


t = LeBonCoin()
t.ParsePage("http://www.leboncoin.fr/ventes_immobilieres/offres/",4)
print t.VoirAnnonces()


