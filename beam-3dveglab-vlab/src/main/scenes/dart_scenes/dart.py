#
# Copyright (C) 2010-2015 Netcetera Switzerland (info@netcetera.com)
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

import sys, math, time

class VLAB:
  def me():
    nm = ''
    try:
      raise ZeroDivisionError
    except ZeroDivisionError:
      nm = sys.exc_info()[2].tb_frame.f_back.f_code.co_name
    return nm+'()'
  me = staticmethod(me)
  def copyfile(source, dest, buffer_size=1024*1024):
    """ Copy a file from source to dest """
    if not hasattr(source, 'read'):
        source = open(source, 'rb')
    if not hasattr(dest, 'write'):
        dest = open(dest, 'wb')
    while 1:
        copy_buffer = source.read(buffer_size)
        if copy_buffer:
            dest.write(copy_buffer)
        else:
            break
    source.close()
    dest.close()
  copyfile = staticmethod(copyfile)

class dobrdf:
  def _writeMaket(self, args):
    # defaults
    q = {
    'fname' : 'maket.xml',
      'alt' : '0.7008782',
      'lat' : '47.478707259',
      'lon' : '8.363187271',
    'cdimx' : '1.0',
    'cdimz' : '1.0',
    'sdimx' : '30.0',
    'sdimy' : '30.0'
    }
    for a in args:
      q[a] = args[a]

    mdata = '''
<?xml version="1.0" encoding="UTF-8"?>
<DartFile version="5.4.3">
    <Maket dartZone="0" exactlyPeriodicScene="2">
        <Scene>
            <CellDimensions x="%s" z="%s"/>
            <SceneDimensions x="%s" y="%s"/>
        </Scene>
        <Soil>
            <OpticalPropertyLink ident="Unvegetated" indexFctPhase="1" type="0"/>
            <ThermalPropertyLink
                idTemperature="thermal_function_290_310" indexTemperature="0"/>
            <Topography presenceOfTopography="1">
                <TopographyProperties fileName="DEM.mp#"/>
            </Topography>
            <DEM_properties createTopography="1">
                <DEMGenerator caseDEM="5" outputFileName="DEM.mp#">
                    <DEM_5 dataEncoding="0" dataFormat="8" fileName="dtm.bin"/>
                </DEMGenerator>
            </DEM_properties>
        </Soil>
        <LatLon altitude="%s" latitude="%s" longitude="%s"/>
    </Maket>
</DartFile>
'''[1:-1] % (q['cdimx'],q['cdimz'],q['sdimx'],q['sdimy'],q['alt'],q['lat'],q['lon'])
    try:
      VLAB.copyfile(q['fname'], '%s_%s' % (q['fname'], time.time()))
    except Exception:
      if not sys.platform.startswith('java'):
        sys.exc_clear()
    fp = open(q['fname'], 'w')
    fp.write(mdata)
    fp.close()

  def _writePhase(self, args):
    # defaults
    q = {
       'fname' : 'phase.xml',
      'sensor' : 'MSI',
       'bands' : '1, 2, 3, 4, 5, 6, 7, 8, 9, 10'
    }
    for a in args:
      q[a] = args[a]
    pdata = '''
<?xml version="1.0" encoding="UTF-8"?>
<DartFile version="5.4.3">
    <Phase expertMode="0">
        <DartInputParameters calculatorMethod="0">
            <nodefluxtracking gaussSiedelAcceleratingTechnique="1" numberOfIteration="4"/>
            <SpectralDomainTir temperatureMode="0">
                <Atmosphere_1 SKYLForTemperatureAssignation="0.0"/>
            </SpectralDomainTir>
            <SpectralIntervals>
                <SpectralIntervalsProperties bandNumber="0"
                    deltaLambda="0.005493" meanLambda="0.56925"
                    radiativeBudgetProducts="0" spectralDartMode="0"/>
            </SpectralIntervals>
            <ExpertModeZone albedoThreshold="1.0E-5"
                illuminationRepartitionMode="2"
                lightPropagationThreshold="1.0E-4"
                nbRandomPointsPerInteceptionAtmosphere="10"
                nbSubSubcenterTurbidEmission="40"
                nbSubcenterIllumination="10" nbSubcenterVolume="2"/>
            <nodeIlluminationMode illuminationMode="0" irradianceMode="1">
                <irradianceDatabaseNode irradianceDatabase="TOASolarIrradiance.txt"/>
            </nodeIlluminationMode>
        </DartInputParameters>
        <DartProduct>
            <dartModuleProducts allIterationsProducts="0"
                brfProducts="1" lidarProducts="0"
                order1Products="0" radiativeBudgetProducts="0">
                <BrfProductsProperties brfProduct="1" extrapolation="1"
                    horizontalOversampling="1" image="1"
                    luminanceProducts="1" maximalThetaImages="0.1"
                    nb_scene="1" outputHapkeFile="0" projection="1"
                    sensorOversampling="1" sensorPlaneprojection="0">
                    <ExpertModeZone_Etalement etalement="2"/>
                    <ExpertModeZone_maskProjection mask_projection="0"/>
                </BrfProductsProperties>
            </dartModuleProducts>
            <maketModuleProducts MNEProducts="0" areaMaketProducts="0"
                coverRateProducts="0" laiProducts="0"/>
        </DartProduct>
    </Phase>
</DartFile>
'''[1:-1] % ()
    try:
      VLAB.copyfile(q['fname'], '%s_%s' % (q['fname'], time.time()))
    except Exception:
      if not sys.platform.startswith('java'):
        sys.exc_clear()
    fp = open(q['fname'], 'w')
    fp.write(pdata)
    fp.close()

  def _writeAtmosphere(self, args):
    # defaults
    q = {
    'fname' : 'atmosphere.xml',
'dayofyear' : '214',
       'lat': '47.4781',
       'lon': '8.3650',
    'co2mix': '1.6',
   'amodel' : 'Rural',
  'amodidx' : '1',
 'h2ovapor' : '0.0',
    'o3col' : '300'
    }
    for a in args:
      if a == 'amodel':
        if args[a] == 'Maritime':
          amodidx='x'
        elif args[a] == 'Urban':
          amodidx='x'
        elif args[a] == 'Trophospheric':
          amodidx='x'
        else:
          amodidx='1'
      else:
        q[a] = args[a]
    adata = '''
<?xml version="1.0" encoding="UTF-8"?>
<DartFile version="5.4.3">
    <Atmosphere atmosphereType="4" rtInBASimulation="0">
        <AtmosphereIterations>
            <AtmosphereTransfertFunctions inputOutputTransfertFunctions="0"/>
            <AtmosphereProducts atmosphereBRF_TOA="1"
                atmosphereRadiance_BOA_apresCouplage="0"
                atmosphereRadiance_BOA_avantCouplage="0" ordreUnAtmos="0"/>
            <AtmosphereComponents downwardingFluxes="0" upwardingFluxes="0"/>
            <AtmosphereExpertModeZone extrapol_atmos="1"
                seuilEclairementAtmos="0.00001" seuilFTAtmos="0.0001"/>
        </AtmosphereIterations>
        <AtmosphereGeometry discretisationAtmos="2" heightOfSensor="3.484"/>
        <AtmosphericOpticalPropertyModel aerosolModel="1"
            aerosolOptDepthFactor="1" atmosphericModel="%s"
            correctionBandModel="1" databaseFileName="atmosphereDatabase.txt"/>
    </Atmosphere>
</DartFile>
'''[1:-1] % (q['amodidx'])
    try:
      VLAB.copyfile(q['fname'], '%s_%s' % (q['fname'], time.time()))
    except Exception:
      if not sys.platform.startswith('java'):
        sys.exc_clear()
    fp = open(q['fname'], 'w')
    fp.write(adata)
    fp.close()

  def _writeDirections(self, args):
    # defaults
    q = {
   'fname' : 'directions.xml',
      'sz' : '27.1',
      'sa' : '32.6'
    }
    for a in args:
      q[a] = args[a]
    ddata = '''
<DartFile version="5.4.3">
    <Directions exactDate="2" ifCosWeighted="1" numberOfPropagationDirections="100">
        <ExpertModeZone numberOfAngularSector="10" numberOfLayers="0"/>
        <SunViewingAngles sunViewingAzimuthAngle="%s" sunViewingZenithAngle="%s"/>
        <HotSpotProperties hotSpotParallelPlane="0"
            hotSpotPerpendicularPlane="0" oversampleDownwardRegion="0" oversampleUpwardRegion="0"/>
        <AddedDirections directionType="0" ifSquareShape="1" imageDirection="1">
            <ZenithAzimuth directionAzimuthalAngle="207.2" directionZenithalAngle="5.75"/>
            <Square widthDefinition="0">
                <DefineOmega omega="0.0010"/>
            </Square>
        </AddedDirections>
    </Directions>
</DartFile>
'''[1:-1] % (q['sa'], q['sz'])
    try:
      VLAB.copyfile(q['fname'], '%s_%s' % (q['fname'], time.time()))
    except Exception:
      if not sys.platform.startswith('java'):
        sys.exc_clear()
    fp = open(q['fname'], 'w')
    fp.write(ddata)
    fp.close()

  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

    args = {
      'lat': '12.3456789',
      'lon': '0.123456789',
    }
    self._writeMaket(args)
    args = {
    'dayofyear' : '214',
           'lat': '47.4781',
           'lon': '8.3650',
        'co2mix': '1.6',
       'amodel' : 'Rural',
     'h2ovapor' : '0.0',
        'o3col' : '300'
    }
    self._writeAtmosphere(args)

    args = {
    }
    self._writePhase(args)

    args = {
      'sz' : '27.1',
      'sa' : '32.6',
    }
    self._writeDirections(args)

class plot:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

class rpv_invert:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

class dolibradtran:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

# Test

dobrdf = dobrdf()
plot = plot()
rpv_invert = rpv_invert()
dolibradtran = dolibradtran()

args = {
         'v' : True,
        'wb' : 'Sequence_MSI.xml',
    'outdir' : 'outdir'
}
dobrdf.main(args)

args = {
         'v' : True,
        'wb' : 'Sequence_MSI.xml',
    'angles' : 'angle.rpv.cosDOM.dat',
   'rootdir' : 'rpv.rami/result.HET01_DIS_UNI_NIR_20'
}
plot.main(args)

args = {
         'v' : True,
     'three' : True,
      'plot' : True,
  'datafile' : 'datafile',
 'paramfile' : 'paramfile',
  'plotfile' : 'plotfile'
}
rpv_invert.main(args)

args = {
         'v' : True,
  'plotfile' : 'plotfile',
       'lat' : 50,
       'lon' : 0,
      'time' : '2013 0601 12 00 00',
    'outdir' : 'outdir'
}
dolibradtran.main(args)
