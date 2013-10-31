#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/
# 
# @(#) $Id: $
#
# Authors: Nicolas Lauret, Fabian Schneider
#
# converted to "BEAM-limited jython" by Jason Brazile
#
#==============================================================================
#title            :DARTDao.py
#description      :This script can be used to recover DART images and spectral bands
#coding       :utf-8
#author           :Nicolas Lauret, (Fabian Schneider)
#date             :20130328
#version          :1.0
#usage            :see DartImages.py
#==============================================================================

import sys, math, array, time, struct
from array import array

# BEAM's jython does not allow: os, string, StringIO

class VLAB:
  def listdir(path):
    if sys.platform.startswith('java'):
      from java.io import File
      return list(File(path).list())
    else:
      import os
      return os.listdir(path)
  listdir = staticmethod(listdir)
  def getenv(key, default=None):
    if sys.platform.startswith('java'):
      from java.lang.System import getenv
      return getenv(key)
    else:
      import os
      return os.getenv(key)
  getenv = staticmethod(getenv)
  class path:
    def exists(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).exists()
      else:
        import os
        return os.path.exists(path)
    exists = staticmethod(exists)
    def isabs(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).isAbsolute()
      else:
        import os
        return os.path.isabs(path)
    isabs = staticmethod(isabs)
    def isdir(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).isDirectory()
      else:
        import os
        return os.path.isdir(path)
    isdir = staticmethod(isdir)
    def join(path, *args):
      if sys.platform.startswith('java'):
        from java.io import File
        f = File(path)
        for a in args:
          g = File(a)
          if g.isAbsolute() or len(f.getPath()) == 0:
            f = g
          else:
            f = File(f, a)
        return f.getPath()
      else:
        import os
        return os.path.join(path, *args)
    join = staticmethod(join)
    def isfile(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).isfile()
      else:
        import os
        return os.path.isfile(path)
    isfile = staticmethod(isfile)
    def normcase(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).getPath()
      else:
        import os
        return os.path.normcase(path)
    normcase = staticmethod(normcase)
    def normpath(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).getCanonicalPath()
      else:
        import os
        return os.path.normpath(path)
    normpath = staticmethod(normpath)
    def split(path):
      if sys.platform.startswith('java'):
        from java.io import File
        f=File(path)
        d=f.getParent()
        if not d:
          if f.isAbsolute():
            d = path
          else:
            d = ""
        return (d, f.getName())
      else:
        import os
        return os.path.split(path)
    split = staticmethod(split)

def enum(**enums):
  return type('Enum', (), enums)

ProjectionPlane = enum(SENSOR_PLANE=0, ORTHOPROJECTION=1, BOA_PLANE=2)
DataUnit = enum(BRF_TAPP=0, RADIANCE=1)
DataLevel = enum(BOA=0, SENSOR=1, TOA=2, ATMOSPHERE_ONLY=3)
SpectralBandMode = enum(VISIBLE=0, VISIBLE_AND_THERMAL=1, THERMAL=2)

class DARTEnv : 
  dartLocal = VLAB.getenv('DART_LOCAL')
  #dartLocal = 'F:\\dart_local\\'
  
  simulationsDirectory = 'simulations'
  
  inputDirectory = 'input'
  outputDirectory = 'output'
  sequenceDirectory = 'sequence'
  
  libPhaseDirectory = 'lib_phase'
  bandRootDirectory = 'BAND'
  
  brfDirectory = 'BRF'
  tappDirectory = 'Tapp'
  radianceDirectory = 'Radiance'
  
  toaDirectory = 'TOA'
  radiativeBudgetDirectory = 'RADIATIVE_BUDGET'
  
  iterRootDirectory = 'ITER'
  couplDirectory = 'COUPL'
  sensorDirectory = 'SENSOR'
  
  #imageDirectoy = VLAB.path.join('IMAGES_DART', 'Non_Projected_Image')
  imageDirectoy = 'IMAGES_DART'
  orthoProjectedImageDirectory = 'IMAGE_PROJETEE'
  nonProjectedImageDirectory = 'Non_Projected_Image'
  
  brfFile = 'brf'
  radianceFile = 'radiance'
  radianceAtmoFile = 'AtmosphereRadiance'
  tappFile = 'tapp'
  radiativeBudgetFile = 'RadiativeBudget'
  
  propertiesFile = 'simulation.properties.txt'

# Class SpectralBand
class SpectralBand:
  def __init__(self) :
    self.index = 0
    self.lambdaMin = 0.
    self.lambdaMax = 0.
    self.mode = SpectralBandMode.VISIBLE
  
  def __str__(self):
    return 'SpectralBand(' + str(self.index) + ': [' + str(self.lambdaMin) + '; ' + str(self.lambdaMax) + ']; ' + str(self.mode) + ')'
  
  def getCentralWaveLength(self):
    return (self.lambdaMax + self.lambdaMin) / 2.
  
  def getBandWidth(self):
    return (self.lambdaMax - self.lambdaMin)

# Class Direction
class Direction :
  def __init__(self, theta, phi, solidAngle = 1, angularSector = 1, index = -1) :
    self.theta = theta
    self.phi = phi
    self.solidAngle = solidAngle
    self.angularSector = angularSector
    self.index = index
  
  def __str__(self):
    return 'Direction(' + str(self.theta) + ', ' + str(self.phi) + ')'
  
  def equal(self, dir2) :
    return abs(self.theta - dir2.theta) < 0.001 and abs(self.phi - dir2.phi) < 0.001

# Class BRF, Tapp, Radiance, per direction
class BRF :
  def __init__(self) :
    self.valeursParDirections = []
  
  def __str__(self):
    string = '<BDAverage'
    for (direction, moyenne) in self.valeursParDirections :
      string += '\n' + str(direction) + ' : ' + str(moyenne)
    string += '>'
    return string
  
  def addValeurDansDirection (self, direction, valeur) :
    self.valeursParDirections.append((direction, valeur))
  
  def getValueForDirection(self, directionRecherchee) :
    for (directionCourante, valeurCourante) in self.valeursParDirections :
      if (directionCourante.equal(directionRecherchee)) :
        return valeurCourante
  
  def getValue(self, indiceDirection) :
    return self.valeursParDirections[indiceDirection]

# Classe Images par direction
class Images :
  def __init__(self) :
    self.matrice2DparDirections = []
  
  def addMatriceDansDirection (self, direction, matrice) :
    self.matrice2DparDirections.append((direction, matrice))
  
  def getMatrice2D(self, directionRecherchee) :
    for (directionCourante, matriceCourante) in self.matrice2DparDirections :
      if (directionCourante.equal(directionRecherchee)) :
        return matriceCourante

# Classe Bilan Radiatif par type
class BilanRadiatif :
  def __init__(self) :
    self.matriceParType = []
  
  def getTypeBilan(self) :
    typeBilans = []
    for (typeBilanCourant, matriceCourante) in self.matriceParType :
      typeBilans.append(typeBilanCourant)
    return typeBilans
  
  def contientTypeBilan(self, typeBilan) :
    for (typeBilanCourant, matriceCourante) in self.matriceParType :
      if typeBilanCourant == typeBilan :
        return True
    return False

def getModeFromString(modeString):
  if modeString == 'T':
    return SpectralBandMode.THERMAL
  elif modeString == 'R+T':
    return SpectralBandMode.VISIBLE_AND_THERMAL
  else :
    return SpectralBandMode.VISIBLE

def getNumMaxIteration(path) :
  dirList = [f for f in VLAB.listdir(path) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(path, f))) and f.startswith(DARTEnv.iterRootDirectory) and f != DARTEnv.iterRootDirectory + 'X']
  
  maxIter = -1
  for rep in dirList :
    numIter = int(rep.split(DARTEnv.iterRootDirectory)[1])
  if numIter > maxIter :
    maxIter = numIter
  return maxIter

def readProperties(propertyPath):
  # propFile= file(propertyPath, "rU" )
  propFile= file(propertyPath, "r" )
  propDict= dict()
  for propLine in propFile:
    propDef= propLine.strip()
    if len(propDef) == 0:
      continue
    if propDef[0] in ( '!', '#' ):
      continue
    punctuation= [ propDef.find(c) for c in ':= ' ] + [ len(propDef) ]
    found= min( [ pos for pos in punctuation if pos != -1 ] )
    name= propDef[:found].rstrip()
    value= propDef[found:].lstrip(":= ").rstrip()
    propDict[name]= value
  propFile.close()
  return propDict;

def readPropertiesFromFile(stringFile):
  properties = StringIO.StringIO(stringFile)
  propertiesLines = properties.readlines()
  propertiesDico = {}
  for line in propertiesLines:
    prop,valeur = line.rstrip("\n\r\t").split(':')[0],line.rstrip("\n\r\t").split(':')[1]
    propertiesDico[prop] = valeur
  return propertiesDico

class DARTSimulation :
  def __init__(self, name, rootSimulations) :
    self.name = name
    self.rootSimulationsDirectory = rootSimulations
  
  def __str__(self):
    return self.name
  
  def getAbsolutePath(self) :
    return VLAB.path.join(self.rootSimulationsDirectory.getAbsolutePath(), self.name)
  
  def isValid(self) :
    if self.name != '' and VLAB.path.exists(self.getAbsolutePath()) :
      dirList=[f for f in VLAB.listdir(self.getAbsolutePath()) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(self.getAbsolutePath(), f)))]
      for directory in dirList:
        # On test si le dossier contient des dossiers output, input et/ou sequence
        # On relance la methode recursivement sur les eventuels autres dossiers (hors input, output et sequence)
        if (directory == DARTEnv.inputDirectory) or (directory == DARTEnv.outputDirectory) or (directory == DARTEnv.sequenceDirectory) :
          return True
    return False
  
  def getProperties(self):
    return readProperties(VLAB.path.join(self.getAbsolutePath(), DARTEnv.outputDirectory, DARTEnv.propertiesFile))
  
  def getSpectralBands(self):   
    properties = self.getProperties()
    nbSpectralBand = int(properties['phase.nbSpectralBands'])
    bandes = []
    for numBand in range(nbSpectralBand):
      bande = SpectralBand()
      bande.index = numBand
      bande.lambdaMin = float(properties['dart.band' + str(numBand) + '.lambdaMin'])
      bande.lambdaMax = float(properties['dart.band' + str(numBand) + '.lambdaMax'])
      bande.mode = getModeFromString(properties['dart.band' + str(numBand) + '.mode'])
      bandes.append(bande)
    return bandes
  
  def getSceneGeolocation(self) :
    properties = self.getProperties()
    return (float(properties['dart.maket.latitude']), float(properties['dart.maket.longitude']))
  
  def getDiscretizedDirection(self):    
    properties = self.getProperties()
    nbDD = int(properties['direction.numberOfDirections'])
    discretizedDirections = []
    for i in range(nbDD) :
      discretizedDirections.append(Direction(float(properties['direction.direction' + str(i) +'.thetaCenter']), float(properties['direction.direction' + str(i) +'.phiCenter']), solidAngle = float(properties['direction.direction' + str(i) +'.omega']), angularSector = int(properties['direction.direction' + str(i) +'.angularSector']), index = i))
    return discretizedDirections
  
  def getUserDirections(self) :
    properties = self.getProperties()
    nbUD = int(properties['direction.nbOfAdditionalSpots'])
    userDirections = []
    for i in range(nbUD) :
      additionalSpotIndex = int(properties['direction.additionalSpot' + str(i) + '.directionIndex'])
      userDirections.append(Direction(float(properties['direction.direction' + str(additionalSpotIndex) +'.thetaCenter']), float(properties['direction.direction' + str(additionalSpotIndex) +'.phiCenter']), index = additionalSpotIndex))
    return userDirections
  
  def listNomsSequences(self) :
    sequencePath = VLAB.path.join(self.getAbsolutePath(), DARTEnv.sequenceDirectory)
    listNom = []
    if (VLAB.path.exists(sequencePath)) :
      dirList=[f for f in VLAB.listdir(sequencePath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(sequencePath, f)))]
      for sequence in dirList :
        nomSequence = sequence.rpartition('_')[0]
        if (not nomSequence in listNom) :
          listNom.append(nomSequence)
    listNom.sort()
    return listNom
  
  def listSequences(self, nom) :
    sequencePath = VLAB.path.join(self.getAbsolutePath(), DARTEnv.sequenceDirectory)
    listSequence = [f for f in VLAB.listdir(sequencePath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(sequencePath, f))) and f.startswith(nom + '_')]
    
    listSequence.sort(lambda a, b: cmp(int(a[len(nom)+1:]),int(b[len(nom)+1:])))
    listSimuSequence = [DARTSimulation(VLAB.path.join(self.name, DARTEnv.sequenceDirectory, s), self.rootSimulationsDirectory) for s in listSequence]
    return listSimuSequence
  
  def getSequence(self, nomSequence, numeroSequence) :
    return DARTSimulation(VLAB.path.join(self.name, DARTEnv.sequenceDirectory, nomSequence + '_' + str(numeroSequence)), self.rootSimulationsDirectory);
  
  def getSubdirectory(self, spectralBand = 0, dataType = DataUnit.BRF_TAPP, level = DataLevel.BOA, iteration = 'last') :
    simulationPath = self.getAbsolutePath()
    bandPath = VLAB.path.join(simulationPath, DARTEnv.outputDirectory, DARTEnv.bandRootDirectory + str(spectralBand))
    brfPath = ''
    if dataType == DataUnit.RADIANCE :
      brfPath = VLAB.path.join(bandPath, DARTEnv.radianceDirectory)
      if (level == DataLevel.TOA or level == DataLevel.ATMOSPHERE_ONLY) :
        brfPath = VLAB.path.join(brfPath, DARTEnv.toaDirectory) # Radiance/TOA
      elif (level == DataLevel.SENSOR) :
        brfPath = VLAB.path.join(brfPath, DARTEnv.sensorDirectory) # Radiance/SENSOR
      elif (not iteration == 'last') :
        brfPath = VLAB.path.join(brfPath, iteration) # Radiance/ITER...
      else :
        # Recherche du dossier COUPL
        tmpPath = VLAB.path.join(brfPath, DARTEnv.couplDirectory) # Radiance/COUPL
        if (not VLAB.path.exists(tmpPath)) :
        # Recherche du dossier ITERX
          tmpPath = VLAB.path.join(brfPath, DARTEnv.iterRootDirectory + 'X') # Radiance/ITERX
          if (not VLAB.path.exists(tmpPath)) :
            # Recherche du dossier ITER de plus fort nombre
            tmpPath = VLAB.path.join(brfPath, DARTEnv.iterRootDirectory + str(getNumMaxIteration(brfPath)))
        brfPath = tmpPath;
    else :
      if (level == DataLevel.BOA) :
        # Test de la presence d'un dossier brf, sinon tapp
        brfPath = VLAB.path.join(bandPath, DARTEnv.brfDirectory)
        if (not VLAB.path.exists(brfPath)) :
          # on essaie le dossier tapp
          brfPath = VLAB.path.join(bandPath, DARTEnv.tappDirectory)
        if (not iteration == 'last') :
          brfPath = VLAB.path.join(brfPath, iteration) # BRF_TAPP/ITER...
        else :
          tmpPath = VLAB.path.join(brfPath, DARTEnv.couplDirectory) # BRF_TAPP/COUPL
          if (not VLAB.path.exists(tmpPath)) :
            # Recherche du dossier ITERX
            tmpPath = VLAB.path.join(brfPath, DARTEnv.iterRootDirectory + 'X') # BRF_TAPP/ITERX
            if (not VLAB.path.exists(tmpPath)) :
              # Recherche du dossier ITER de plus fort nombre
              tmpPath = VLAB.path.join(brfPath, DARTEnv.iterRootDirectory + str(getNumMaxIteration(brfPath)))
          brfPath = tmpPath;
      elif (level == DataLevel.SENSOR) :
        brfPath = VLAB.path.join(bandPath, DARTEnv.sensorDirectory) # SENSOR
      else :
        brfPath = VLAB.path.join(bandPath, DARTEnv.toaDirectory) # TOA
    
    return brfPath
  
  def getAveragePerDirection(self, spectralBand = 0, dataType = DataUnit.BRF_TAPP, level = DataLevel.BOA, iteration = 'last') :
    brfPath = self.getSubdirectory(spectralBand, dataType, level, iteration)
    brf = BRF()
    if (VLAB.path.exists(brfPath)) :
      # recherche du nom de fichier contenant le brf/tapp/radiance
      if (dataType == DataUnit.RADIANCE) :
        if (level == DataLevel.ATMOSPHERE_ONLY):
          brfPath = VLAB.path.join(brfPath, DARTEnv.radianceAtmoFile)
        else:
          brfPath = VLAB.path.join(brfPath, DARTEnv.radianceFile)
      else :
        tmpPath = VLAB.path.join(brfPath, DARTEnv.brfFile)
        if (not VLAB.path.exists(tmpPath)) :
          tmpPath = VLAB.path.join(brfPath, DARTEnv.tappFile)
        brfPath = tmpPath
      
      if (VLAB.path.exists(brfPath) and VLAB.path.isfile(brfPath)) :
        # lecture du fichier et remplissage du conteneur
        fichierBRF = open(brfPath, "r")
        lines = fichierBRF.readlines()
        for line in lines :
          split = line.split()
          brf.addValeurDansDirection(Direction(float(split[0]), float(split[1])), float(split[2]))
        fichierBRF.close()
    return brf
  
  def getImageNameInDirection(self, direction):
    properties = self.getProperties()
    imageNumber = properties['dart.products.images.number']
    imageIndex = 0
    found = False
    imageName = None
    while (imageIndex < imageNumber and not found):
      directionIndex = int(properties['dart.products.image' + str(imageIndex) + '.directionIndex'])
      if (directionIndex == direction.index):
        imageName = properties['dart.products.image' + str(imageIndex) + '.name']
        found = True
      else:
        imageIndex = imageIndex + 1
    return imageName
  
  def getImageMinMaxInDirection(self, direction, spectralBand = 0, dataType = DataUnit.BRF_TAPP, level = DataLevel.BOA, iteration = 'last', projectionPlane=ProjectionPlane.SENSOR_PLANE) :
    brfPath = self.getSubdirectory(spectralBand, dataType, level, iteration)
    minImage = None
    maxImage = None
    if (VLAB.path.exists(brfPath)) :
      imageDirPath = VLAB.path.join(brfPath, DARTEnv.imageDirectoy)
      if (projectionPlane == ProjectionPlane.ORTHOPROJECTION):
        imageDirPath = VLAB.path.join(imageDirPath, DARTEnv.orthoProjectedImageDirectory)
      elif (projectionPlane == ProjectionPlane.BOA_PLANE):
        imageDirPath = VLAB.path.join(imageDirPath, DARTEnv.nonProjectedImageDirectory)
      imageName = self.getImageNameInDirection(direction)
      mprPath = VLAB.path.join(imageDirPath, imageName + '.mpr')
      if (VLAB.path.exists(mprPath)):
        mprFile = open(mprPath, "r")
        lines = mprFile.readlines()
        for line in lines :
          split = line.split('=')
          if (split[0].startswith('MinMax')):
            splitSplit = split[1].split(':')
            minImage = float(splitSplit[0])
            maxImage = float(splitSplit[1])
            mprFile.close()
            return (minImage, maxImage)
        mprFile.close()
    return (minImage, maxImage)

  def getImageInDirection(self, direction, spectralBand = 0, dataType = DataUnit.BRF_TAPP, level = DataLevel.BOA, iteration = 'last', projectionPlane=ProjectionPlane.SENSOR_PLANE):
    brfPath = self.getSubdirectory(spectralBand, dataType, level, iteration)
    data = []
    if (VLAB.path.exists(brfPath)):
      imageDirPath = VLAB.path.join(brfPath, DARTEnv.imageDirectoy)
      if (projectionPlane == ProjectionPlane.ORTHOPROJECTION):
        imageDirPath = VLAB.path.join(imageDirPath, DARTEnv.orthoProjectedImageDirectory)
      elif (projectionPlane == ProjectionPlane.BOA_PLANE):
        imageDirPath = VLAB.path.join(imageDirPath, DARTEnv.nonProjectedImageDirectory)
      imageName = self.getImageNameInDirection(direction)
      # Recovery of the size of the image, in pixels
      mprPath = VLAB.path.join(imageDirPath, imageName + '.mpr')
      if (VLAB.path.exists(mprPath)):
        sizeX = 0
        sizeY = 0
        mprFile = open(mprPath, "r")
        lines = mprFile.readlines()
        for line in lines:
          split = line.split('=')
          if (split[0].startswith('Size')):
            splitSplit = split[1].split(' ')
            sizeX = int(splitSplit[0])
            sizeY = int(splitSplit[1])
        mprFile.close()
        mpSharpPath = VLAB.path.join(imageDirPath, imageName + '.mp#')
        if (VLAB.path.exists(mpSharpPath)):
          mpSharpFile = open(mpSharpPath, "rb")
          for x in range(sizeX):
            line = []
            for y in range(sizeY):
              line.append(struct.unpack('d', mpSharpFile.read(8))[0])
            data.append(line)
          mpSharpFile.close()
    return data

class DARTRootSimulationDirectory :
  def __init__(self) :
    pass
  
  def samefile(self, path1, path2) :
    return VLAB.path.normcase(VLAB.path.normpath(path1)) == VLAB.path.normcase(VLAB.path.normpath(path2))
  
  def getAbsolutePath(self) :
    return VLAB.path.join(DARTEnv.dartLocal, DARTEnv.simulationsDirectory)
  
  def getSimulationsList(self) :
    rootSimulationPath = self.getAbsolutePath()
    # Liste de tous les fichier/dossier non cache du repertoire
    dirList=[f for f in VLAB.listdir(rootSimulationPath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(rootSimulationPath, f)))]
    dirList.sort()
    listSimulations = []
    for directory in dirList:
      self.listSimulationsInPath(listSimulations, directory)
    return listSimulations
  
  def listSimulationsInPath(self, listSimulations, path) :
    rootPath = path
    if not VLAB.path.isabs(path):
      rootPath = VLAB.path.join(self.getAbsolutePath(), path)
    dirList=[f for f in VLAB.listdir(rootPath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(rootPath, f)))]
    dirList.sort()
    
    isSimulation = False    
    for directory in dirList:
      # On test si le dossier contient des dossiers output, input et/ou sequence
      # On relance la methode recursivement sur les eventuels autres dossiers (hors input, output et sequence)
      if (directory != DARTEnv.inputDirectory) and (directory != DARTEnv.outputDirectory) and (directory != DARTEnv.sequenceDirectory) :
        self.listSimulationsInPath(listSimulations, VLAB.path.join(path, directory))
      else :
        isSimulation = True
    if isSimulation :
      self.addSimulation(listSimulations, path)
  
  def addSimulation(self, listSimulations, path):
    simulation = self.getSimulation(path)
    if simulation.isValid() :
      listSimulations.append(simulation)
  
  def getSimulation(self, name) :
    rootSimulationPath = self.getAbsolutePath()
    rootPath = name
    if not VLAB.path.isabs(name):
      rootPath = VLAB.path.join(rootSimulationPath, name)
    simulationName = ''
    if not VLAB.path.exists(rootPath) :
      simulationName = name
    elif not self.samefile(rootPath, rootSimulationPath) :
      if VLAB.path.isdir(rootPath):
        (head, tail) = VLAB.path.split(rootPath)
        while not self.samefile(head, rootSimulationPath) and head !='' :
          simulationName = VLAB.path.join(tail, simulationName)
          (head, tail) = VLAB.path.split(head)
        else :
          if head != '' :
            simulationName = VLAB.path.join(tail, simulationName)
          else :
            simulationName = ''
    return DARTSimulation(simulationName, self)

class DARTDao :
  def __init__(self) :
    pass
  
  def getRootSimulationDirectory(self) :
    return DARTRootSimulationDirectory()
    
  def getSimulationsList(self) :
    return self.getRootSimulationDirectory().getSimulationsList()
  
  def getSimulation(self, name) :
    return self.getRootSimulationDirectory().getSimulation(name)

def Bandes(simulationProperties):
  propertiesDico = readPropertiesFromFile(simulationProperties)
  i = int(propertiesDico['phase.nbSpectralBands'])
  bandes = []
  for j in range(i):
    bande = {}
    bande['spectralBandwidth'] = round(float(propertiesDico['dart.band' + str(j) + '.lambdaMax']) - float(propertiesDico['dart.band' + str(j) + '.lambdaMin']),4)
    a = float(propertiesDico['dart.band' + str(j) + '.lambdaMin']) + bande['spectralBandwidth'] / 2
    bande['centralWavelength'] = round(float(a),4)
    bande['mode'] = propertiesDico['dart.band' + str(j) + '.mode']
    bandes.append(bande)
  return bandes

#==============================================================================
#title            :DartImages.py
#description      :This script can be used to write a *.bsq binary file and a corresponding ENVI header *.hdr from DART output images
#required scripts :DARTDao.py
#author           :Fabian Schneider, Nicolas Lauret
#date             :20130328
#version          :1.0
#usage            :see writeDataCube.py
#==============================================================================


class DartImages :
  def __init__(self) :
    pass

  # http://rightfootin.blogspot.ch/2006/09/more-on-python-flatten.html, based on Mike C. Fletcher's BasicTypes library
  def flatten( self, l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
      while isinstance(l[i], ltypes):
        if not l[i]:
          l.pop(i)
          i -= 1
          break
        else:
          l[i:i + 1] = l[i]
      i += 1
    return ltype(l)

  def getImagesBandsAsList( self, DartInfo, ImageInfo ) :

    simulation = DARTDao().getSimulation( DartInfo.simulationName )

    imagesList = []
    spectralBandsList = []
    
    if DartInfo.isSequence:
      sequencesList = simulation.listSequences( DartInfo.sequenceName )
      
      for sequence in sequencesList:
        # Recover the number of Spectral Band
        spectralBands = sequence.getSpectralBands()
    
        # Recover the Directions
        if ImageInfo.isUserDirection:
          directions = sequence.getUserDirections()
        else:
          directions = simulation.getDiscretizedDirection()
  
        # Recover the images in the defined direction for each spectral band
        for band in spectralBands:
          imagesList.append(sequence.getImageInDirection( directions[ ImageInfo.directionNumber ], band.index, ImageInfo.dataType, ImageInfo.imageLevel, ImageInfo.iteration, ImageInfo.projectionPlane ))
          spectralBandsList.append( band )
    else:
      # Recover the number of Spectral Band
      spectralBands = simulation.getSpectralBands()

      # Recover the Directions
      if ImageInfo.isUserDirection:
        directions = sequence.getUserDirections()
      else:
        directions = simulation.getDiscretizedDirection()

      # Recover the images in the defined direction for each spectral band
      for band in spectralBands:
        imagesList.append(simulation.getImageInDirection( directions[ ImageInfo.directionNumber ], band.index, ImageInfo.dataType, ImageInfo.imageLevel, ImageInfo.iteration, ImageInfo.projectionPlane ))
        spectralBandsList.append( band )

    return imagesList, spectralBandsList
  
  def writeDataCube( self, DartInfo, ImageInfo, HeaderInfo ) :
    
    imagesList, spectralBandsList = self.getImagesBandsAsList( DartInfo, ImageInfo )
    
    # write BSQ binary file
    fout = open( DartInfo.outputFilename + '.bsq', 'wb')
    flatarray = array('f', self.flatten( imagesList ))
    flatarray.tofile(fout)
    fout.close()

    # ENVI header information, more infos on: http://geol.hu/data/online_help/ENVI_Header_Format.html
    samples = len( imagesList[0][0] )
    lines = len( imagesList[0] )
    bands = len( imagesList )
    headerOffset = 0
    fileType = 'ENVI Standard'
    dataType = 4
    interleave = 'BSQ'
    byteOrder = 0
    xStart = 1
    yStart = 1
    defaultBands = '{0}'
    wavelengthUnits = 'Nanometers'
    wavelength = ''
    fwhm = ''
    for band in spectralBandsList:
      wavelength += str( band.getCentralWaveLength()*1000 ) + ', '
      fwhm += str( band.getBandWidth()*1000 ) + ', '

    # write ENVI header file
    fout = open( DartInfo.outputFilename + '.hdr', 'w')
    fout.writelines( 'ENVI ' + '\n' )
    fout.writelines( 'description = { ' + HeaderInfo.description + ' }' + '\n' )
    fout.writelines( 'samples = ' + str( samples ) + '\n' )
    fout.writelines( 'lines = ' + str( lines ) + '\n' )
    fout.writelines( 'bands = ' + str( bands ) + '\n' )
    fout.writelines( 'header offset = ' + str( headerOffset ) + '\n' )
    fout.writelines( 'file type = ' + fileType + '\n' )
    fout.writelines( 'data type = ' + str( dataType ) + '\n' )
    fout.writelines( 'interleave = ' + interleave + '\n' )
    fout.writelines( 'sensor type = ' + HeaderInfo.sensorType + '\n' )
    fout.writelines( 'byte order = ' + str( byteOrder ) + '\n' )
    fout.writelines( 'x start = ' + str( xStart ) + '\n' )
    fout.writelines( 'y start = ' + str( yStart ) + '\n' )
    fout.writelines( 'map info = {' + HeaderInfo.projectionName + ', ' + str( HeaderInfo.xReferencePixel ) + ', ' + str( HeaderInfo.yReferencePixel ) + ', ' + str( HeaderInfo.xReferenceCoordinate ) + ', ' + str( HeaderInfo.yReferenceCoordinate ) + ', ' + str( HeaderInfo.xPixelSize ) + ', ' + str( HeaderInfo.yPixelSize ) + ', ' + HeaderInfo.pixelUnits + ' }' + '\n' )
    fout.writelines( 'default bands = ' + defaultBands + '\n' )
    fout.writelines( 'wavelength units = ' + wavelengthUnits + '\n' )
    fout.writelines( 'wavelength = { ' + wavelength[:-2] + ' }' + '\n' )
    fout.writelines( 'fwhm = { ' + fwhm[:-2] + ' }' + '\n' )
    fout.close()

#==============================================================================
#title            :writeDataCube.py
#description      :This script writes a *.bsq binary file and a corresponding ENVI header *.hdr from DART output images
#required scripts :DartImages.py + DARTDao.py
#author           :Fabian Schneider
#date             :20130328
#version          :1.0
#usage            :python writeDataCube.py
#==============================================================================


class DartInfo :
  
  simulationName = 'DartSimulation30m_Laegeren' # name of the DART simulation
  isSequence = False            # options: True = images shall be restored from a sequence // False = images shall be restored from the simulation output only
  sequenceName = 'sequence_apex'      # name of the sequence within the simulation (if there is one)
  outputFilename = 'DartOutput'     # name of the output file that is written

class ImageInfo :

  imageLevel = DataLevel.SENSOR         # options: BOA = bottom of atmosphere // SENSOR = at sensor // TOA = top of atmosphere // ATMOSPHERE_ONLY
  isUserDirection = False             # options: True = images of a user defined direction // False = images of a discretisized direction
  directionNumber = 0               # number of the direction starting at 0, e.g. 0 = first direction
  dataType = DataUnit.RADIANCE          # options: BRF_TAPP = bidirectional reflectance factor [0 1] // RADIANCE = radiance [W/m2]
  iteration = 'last'                # last iteration product
  projectionPlane=ProjectionPlane.SENSOR_PLANE  # options: SENSOR_PLANE = image in the sensor plane // ORTHOPROJECTION = orthorectified image // BOA_PLANE = non-projected image on the BOA plane

# see more information on http://geol.hu/data/online_help/ENVI_Header_Format.html
class HeaderInfo :

  description = 'some text'       # description of the file
  sensorType = 'APEX'           # specific sensor type like IKONOS, QuickBird, RADARSAT  
  projectionName = 'Arbitrary'      # name of projection, e.g. UTM
  xReferencePixel = 1           # x pixel corresponding to the reference x-coordinate
  yReferencePixel = 1           # y pixel corresponding to the reference y-coordinate
  xReferenceCoordinate = 2669660.0000   # reference pixel x location in file coordinates
  yReferenceCoordinate = 1259210.0000		# reference pixel y location in file coordinates
	xPixelSize = 1							# pixel size in x direction
	yPixelSize = 1							# pixel size in y direction
	pixelUnits = 'units=Meters'

DartImages().writeDataCube( DartInfo, ImageInfo, HeaderInfo )
