#!/usr/bin/env python

################
# Requirements
#
# - cabby 
#   ~$ pip install cabby
#
# - stix==1.1.1.4
#   ~$ git clone https://github.com/CybOXProject/python-cybox.git
#   ~$ cd python-cybox/
#   ~$ git checkout v2.1.0.12
#   ~$ sudo python setup.py install
#
# - cybox==2.1.0.12
#   ~$ git clone https://github.com/STIXProject/python-stix.git
#   ~$ cd python-stix
#   ~$ git checkout v1.1.1.4
#   ~$ sudo python setup.py install 
#
# - stix
#   ~$ pip install stix

##################################
# PUSH degli IoC sulla rete Cyber Saiyan
#
# - Adattare le variabili da riga 66 a riga 75 (esempio con IoC di Emanuele De Lucia)
#
# - Generare il file .stix 
#   ~$ python CS_build_stix.py > your_stix_file.stix
#
# - PUSH del file .stix sulla collection dedicata "community" (la password per il push deve essere richiesta sul gruppo Telegram dedicato)
#   ~$ taxii-push --discovery https://infosharing.cybersaiyan.it:9000/services/discovery --dest community --username community --password TO-BE-SENT --content-file test4.stix
#
# - Verifica degli IoC 
#   ~$ taxii-poll --host infosharing.cybersaiyan.it --https --collection CS-COMMUNITY-TAXII --discovery /taxii-discovery-service


import sys
import os.path
import json
import time
import datetime

from stix.core import STIXPackage, STIXHeader
from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.tlp import TLPMarkingStructure
from stix.common import InformationSource, Identity
from stix.indicator import Indicator

from mixbox.idgen import set_id_namespace
from mixbox.namespaces import Namespace

from cybox.core import Observable
from cybox.common import Hash
from cybox.objects.file_object import File
from cybox.objects.uri_object import URI
from cybox.objects.address_object import Address
from cybox.objects.email_message_object import EmailAddress

def main():
    ######################################################################
    # MODIFICARE LE VARIABILI SEGUENTI

    MyTITLE = "APT28 / Fancy Bear"
    DESCRIPTION = "Emanuele De Lucia - APT28 / Fancy Bear still targeting military institutions - https://www.emanueledelucia.net/apt28-targeting-military-institutions/"

    sha256 = []
    md5 = ['43D7FFD611932CF51D7150B176ECFC29', '549726B8BFB1919A343AC764D48FDC81']
    sha1 = []
    domains = ['beatguitar.com']
    urls = ['https://beatguitar.com/aadv/gJNn/X2/ep/VQOA/3.SMPTE292M/?ct=+lMQKtXi0kf+3MVk38U=', 'https://beatguitar.com/n2qqSy/HPSe0/SY/yAsFy8/mSaYZP/lw.sip/?n=VxL0BnijNmtTnSFIcoQ=']
    ips = ['185.99.133.72']
    emails = []

    ######################################################################

    # Costruzione STIX file
    NAMESPACE = Namespace("https://infosharing.cybersaiyan.it", "CYBERSAIYAN")
    set_id_namespace(NAMESPACE)

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    SHORT = timestamp

    wrapper = STIXPackage()
    info_src = InformationSource()
    info_src.identity = Identity(name="CyberSaiyan Community")
    
    marking_specification = MarkingSpecification()
    marking_specification.controlled_structure = "//node() | //@*"
    tlp = TLPMarkingStructure()
    tlp.color = "WHITE"
    marking_specification.marking_structures.append(tlp)
    
    handling = Marking()
    handling.add_marking(marking_specification)
    
    wrapper.stix_header = STIXHeader(information_source=info_src, title=MyTITLE, description=DESCRIPTION, short_description=SHORT)
    wrapper.stix_header.handling = handling
    
    # HASH indicators
    indicatorHASH = Indicator()
    indicatorHASH.title = MyTITLE + " - HASH"
    indicatorHASH.add_indicator_type("File Hash Watchlist")
    
    for idx, sha256 in enumerate(sha256):
    	filei = File()
        filei.add_hash(Hash(sha256))
    	
        obsi = Observable(filei)
        indicatorHASH.add_observable(obsi)
    
    for idx, md5 in enumerate(md5):
    	filej = File()
        filej.add_hash(Hash(md5))
    	
        obsj = Observable(filej)
        indicatorHASH.add_observable(obsj)

    for idx, sha1 in enumerate(sha1):
    	filek = File()
        filek.add_hash(Hash(sha1))
    	
        obsk = Observable(filek)
        indicatorHASH.add_observable(obsk)
    
    # DOMAIN indicators
    indiDOMAIN = Indicator()
    indiDOMAIN.title = MyTITLE + " - DOMAIN"
    indiDOMAIN.add_indicator_type("Domain Watchlist")

    for idu, domains in enumerate(domains):
        url = URI()
	url.value = domains
	url.type_ =  URI.TYPE_DOMAIN
	url.condition = "Equals"
        
        obsu = Observable(url)
        indiDOMAIN.add_observable(obsu)

    # URL indicators
    indiURL = Indicator()
    indiURL.title = MyTITLE + " - URL"
    indiURL.add_indicator_type("URL Watchlist")

    for idu, urls in enumerate(urls):
        url = URI()
	url.value = urls
	url.type_ =  URI.TYPE_URL
	url.condition = "Equals"

        obsu = Observable(url)
        indiURL.add_observable(obsu)

    # IP indicators
    indiIP = Indicator()
    indiIP.title = MyTITLE + " - IP"
    indiIP.add_indicator_type("IP Watchlist")

    for idu, ips in enumerate(ips):
        ip = Address()
	ip.address_value = ips
        
        obsu = Observable(ip)
        indiIP.add_observable(obsu)

    # EMAIL indicators
    indiEMAIL = Indicator()
    indiEMAIL.title = MyTITLE + " - EMAIL"
    indiEMAIL.add_indicator_type("Malicious E-mail")

    for idu, emails in enumerate(emails):
        email = EmailAddress()
	email.address_value = emails
        
        obsu = Observable(email)
        indiEMAIL.add_observable(obsu)

    # add all indicators
    wrapper.add_indicator(indicatorHASH)
    wrapper.add_indicator(indiDOMAIN)
    wrapper.add_indicator(indiURL)
    wrapper.add_indicator(indiIP)
    wrapper.add_indicator(indiEMAIL)
    
    print(wrapper.to_xml())
    
if __name__ == '__main__':
    main()
