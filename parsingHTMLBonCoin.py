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
from datetime import datetime

#~  import shelve => sauv et lecture obj python


from DiversFonction import *


class LeBonCoin:
    """ Permet de recuperer les annonces le bon coin
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
            html=BeautifulSoup(str(annonce))
            lien_annonce =  html.find_all('a')[0].get('href')
            if "compteperso.leboncoin.fr" not in lien_annonce:
                self.lireAnnonce(lien_annonce)


    def lireAnnonce(self,urlAnnonce):
        br=mechanize.Browser()
        br.set_handle_robots(False)
        page=br.open(urlAnnonce)
        source=page.read()
        soup = BeautifulSoup(source)
        """ListeAllVariable = soup.findAll('script',{'type':"text/javascript"})"""
        ListeAllVariable = soup.findAll('script')
        dico_annonce = {}
        for AllVariable in ListeAllVariable:
            if AllVariable.string != None:
                if 'utag_data' in AllVariable.string:
                    tab_var = AllVariable.string.split('{', 1)[1].rsplit('}', 1)[0].replace('\n','').replace(' ','').replace('"','').split(',')
                    for var in tab_var:
                        dico_annonce[var.split(':')[0]] = var.split(':')[1]
                if 'polygon view, hide carto link'  in AllVariable.string:
                    if 'trim("city ")' in AllVariable.string:
                        geoloc = self.geolocator.geocode('%s %s'%(dico_annonce['city'].replace('_',' '),dico_annonce['cp']),geometry="geojson")
                        location= geoloc.raw['geojson']
                        dico_annonce['location']=location
                        dico_annonce['zone']='zone'
                    if 'trim("address ")' in AllVariable.string:
                        location_annonce = {}
                        location_annonce['type']='Point'
                        longitude = float(AllVariable.string.replace('\n','').replace(' ','').replace('"','').split(';')[1].split('=')[1])
                        latitude = float(AllVariable.string.replace('\n','').replace(' ','').replace('"','').split(';')[0].split('=')[1])
                        location_annonce['coordinates']=[longitude,latitude]
                        dico_annonce['zone']='point'
                        dico_annonce['location'] =location_annonce
        json_annonce = json.dumps(dico_annonce)
        self.liste_annonces.append(json_annonce)


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
        while nb_total_page >= page :
            try:
                self.LirePage(urlPage+"?o=%s"%(page))
            except:
                print "erreur"
            page= page+1
            print "page %s"%(page)

    def VoirAnnonces(self):
        print self.liste_annonces

    def SendAnnoncesElastic(self):
        es = Elasticsearch([{'host': '192.168.1.99', 'port': 9200}])
        for annonces in self.liste_annonces:
            es.index(index='leboncoin',doc_type='annonceimmo',body=annonces)


t = LeBonCoin()
t.ParsePage("http://www.leboncoin.fr/ventes_immobilieres/offres/")
t.SendAnnoncesElastic()


