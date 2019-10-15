__author__ = 'haaroony'

'''

 .d8888b. 888                              .d8888b. 888     d8b .d888888    
d88P  Y88b888                             d88P  Y88b888     Y8Pd88P" 888    
Y88b.     888                             Y88b.     888        888   888    
 "Y888b.  88888b.  8888b. 88888b.  .d88b.  "Y888b.  88888b. 888888888888888 
    "Y88b.888 "88b    "88b888 "88bd8P  Y8b    "Y88b.888 "88b888888   888    
      "888888  888.d888888888  88888888888      "888888  888888888   888    
Y88b  d88P888  888888  888888 d88PY8b.    Y88b  d88P888  888888888   Y88b.  
 "Y8888P" 888  888"Y88888888888P"  "Y8888  "Y8888P" 888  888888888    "Y888 
                          888                                               
                          888                                               
                          888                                              
                          
This is a logger it lets you write to the command line and to a file at the same time

'''

### Logger
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)
logger = logging.getLogger(__name__)
###

def logthis(str):
    logger.info(str)

def logError(str):
    logger.error(str)