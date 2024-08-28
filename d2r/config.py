#This module implements .ini config file parsing, plus several data transformation and
#validation. The core function is read_config(), which requires the .ini infile and
#returns a two (or more) levels dictionary (not a configparser). First level keys are 
#the .ini sections, second level are values.  
#We use the same notation as configparser objects, in particular we refer to "interpolate"
#as the operation of tweaking data, e.g. typing (so that values are actually booleans, int
#and so forth). The main extra functionality injected is the possibility of having lists,
#which are not supported by configparser. When possible we use however configparser
#native interpolation/validation mechanisms

import configparser
import os

class Dataset:
	def __init__(self, title, body):
		#constructor
		self.name = 'stub'
	def to_string(self):
		return('stub')

class Analysis:
	def __init__(self, title, body):
		#constructor
		self.name = 'stub'
	def to_string(self):
		return('stub')

class Render:
	def __init__(self, title, body):
		#constructor
		self.name = 'stub'
	def to_string(self):
		return('stub')


def read_config(infile):
	'''
	Reads the config file in .ini format, parse some data so e.g. there's lists
	and not many keys, returns a dictionary
	'''
	
	#check if file exists
	if not os.path.exists(infile):
		msg = 'Config file does not exist: ' + infile
		raise FileNotFoundError(msg)
	
	#instantiate a configparser object
	config = configparser.ConfigParser(interpolation = configparser.ExtendedInterpolation())
	config.read(infile)
	
	#prepare the output lists, first level of keys
	datasets = []
	analyses = []
	renders = []
	
	#loading everything
	for section in config.sections():
		#breaking up the section name, which should be "OPERATION qual1 <qual2>"
		pieces = section.split()
		if len(pieces) < 2 or len(pieces) > 3:
			msg = 'Bad section name: ' + section
			raise ValueError(msg)
		op = pieces[0]
		title = " ".join(pieces[1:])
		
		#each section is an instance of an object
		found = False
		if op == 'DATA':
			datasets.append(Dataset(title, config[section]))
			found = True
		if op == 'ANALYSIS':
			analyses.append(Analysis(title, config[section]))
			found = True
		if op == 'RENDER':
			renders.append(Render(title, config[section]))
			found = True
		if not found:
			raise ValueError('Bad section name: ' + op)
			
		
		#let's go through each field
		#for key in config[section]:
			#some on-the-fly interpolations for common values in all sections
		#	if key == 'skip_if_already_done':
	#			res[op][opid][key] = config[section].getboolean(key)	
#			else:
				#just copying the value
#				res[op][opid][key] = config[section][key]
	
	return(datasets, analyses, renders)
