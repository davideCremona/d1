# USAGE:

import sys
from itertools import tee, islice, chain, izip
import os.path
from sys import path
path.append("includes/")
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, Element, SubElement
from Task import Task

TAG_ROOT = 'root'
TAG_COMPONENTS = 'components'
TAG_COMPONENT  = 'component'
TAG_LAYER = 'layer'
TAG_NAME  = 'name'
TAG_EDGES = 'edges'
TAG_EDGE  = 'edge'
TAG_FROM  = 'from'
TAG_TO    = 'to'
MAX_LAYER = 3

def previous_and_next(some_iterable) :
	prevs, items, nexts = tee(some_iterable, 3)
	prevs = chain([None], prevs)
	nexts = chain(islice(nexts, 1, None), [None])
	return izip(prevs, items, nexts)

def fileGeneration(filecont, filename, dirname, tasksArray, xmlEdges, outputRoot, outputEdges) :
	#start file generation
	# copy layer 1 edges
	for edge in xmlEdges:
	 	if edge.find(TAG_FROM).find(TAG_NAME).text in textNames[0]:
	 		outputEdges.append(edge)
	# generate layer 2 edges
	for task in tasksArray:
		for edge in task.getConfiguration():
			outputEdges.append(edge)
	# copy other layers
	for edge in xmlEdges:
		name = edge.find(TAG_FROM).find(TAG_NAME).text
		if name not in textNames[0] and name not in textNames[1]:
			outputEdges.append(edge)
	physicFile = open(dirname+"/"+filename+str(filecont)+".xml",'w+')      #open file
	filecont = filecont+1 #increment file counter
	physicFile.write(tostring(outputRoot))             #write file
	outputEdges.clear()
	return filecont
	#end file generation


# if the user called this script in a wrong way, show an error message.
if len(sys.argv) <= 3:
	print "USAGE:"
	print "python <script name> <XML file path> <layer> <output directory>"
else:

	# gets the XML file path and store in xmlPath.
	xmlPath = sys.argv[-3]
	# level of depth
	layer = sys.argv[-2]
	#dirname
	dirname = sys.argv[-1]

	# check if the given xml file exists and then parse it.
	if os.path.isfile(xmlPath):

		#get all the xml in one tree
		xmlTree = ET.parse(xmlPath)
		#gets the root
		xmlRoot = xmlTree.getroot()

		# getting all the names, divided by layer.
		#(needed for the last stage -> file generation)
		xmlNames = []
		textNames = {}
		for i in [0,1,2,3,4]:
			textNames[i] = []
			namesLayerXQuery = "./"+TAG_COMPONENTS+"/"+TAG_COMPONENT+"["+TAG_LAYER+"='"+str(i+1)+"']/"+TAG_NAME
			xmlNames.append(xmlRoot.findall(namesLayerXQuery))
			for xmlName in xmlNames[i]:
				textNames[i].append(xmlName.text)


		#puts all the tasks in a dictionary
		tasks = {}
		for name in xmlNames[int(layer)-1] :
			tasks[name.text] = Task(name.text)

		# gets all the edges
		edgesXQuery = "./"+TAG_EDGES+"/"+TAG_EDGE
		xmlEdges = xmlRoot.findall(edgesXQuery)

		# adds edges to the corresponding task
		for edge in xmlEdges :
			taskName = edge.find(TAG_FROM).find(TAG_NAME).text
			if tasks.has_key(taskName) :
				tasks[taskName].addEdge(edge)

		#adjusting tasks list to have a pointer to the next task
		for prev, item, nxt in previous_and_next(tasks.values()) :
			item.next = nxt

		#now tasks is an hash map with linked elements.

		#preparing the output directory
		if not os.path.isdir(dirname):                     #check if output directory exists
			os.makedirs(dirname)                           #if not, create a new one

		#creating the output XML
		outputRoot = ET.Element(TAG_ROOT)                  #create root
		outputRoot.append((xmlRoot.find(TAG_COMPONENTS)))  #copy components
		outputEdges = SubElement(outputRoot, TAG_EDGES)    #create edges

		#basic filename
		filename = "out"
		#counts the generated files
		filecont = 1
		tasksArray = tasks.values()

		#generating the first xml file that is the first configuration
		#(all the tasks has been initialized with the first configuration
		# when they are created [Task()])
		filecont = fileGeneration(filecont, filename, dirname, tasksArray, xmlEdges, outputRoot, outputEdges)

		#getting the task list head
		result = tasksArray[0]
		while result!=None:
			result = tasksArray[0] #needed due to looping problems

			#take the next task that can change his configuration
			result = result.getNextAvailable()
			if result!=None:
				#change his configuration
				result.setNextConfiguration()
				#generating a new file by passing tasksArray and the other stuffs.
				filecont = fileGeneration(filecont, filename, dirname, tasksArray, xmlEdges, outputRoot, outputEdges)
				#clearing edges for the next file
				outputEdges.clear()

		print "[fileGenerator] Generated #", (filecont-1), "configurations in directory ", dirname

	else:

		print "input file does not exists"
