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
# small script to generate static content pages for the microsite
#

baseurl = 'http://www.geo.uzh.ch/microsite/3dveglab/index.html'

template = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
 <meta name="generator" content=
 "HTML Tidy for Linux (vers 25 March 2009), see www.w3.org" />
 <meta http-equiv="Content-Type" content="text/html; charset=us-ascii" />
 <meta http-equiv="Cache-Control" content=
 "no-transform,public,max-age=300,s-maxage=900" />

 <title>3D Vegetation Lab</title>
 <base href="%s" />
 <style type="text/css" media="screen, print, projection">
/*<![CDATA[*/
 @import url(http://fonts.googleapis.com/css?family=Oxygen:400,700,300);
 html, body   { margin:0; padding:0; color: #333; background:#fff; font-family: Arial,sans-serif; font-size: 14px; line-height: 22px; }
 #body        { margin:0 auto; background:white; }
 #header      { margin:0 auto; background:white; border-bottom: 3px solid #48A17E; }
 #header table 
              { margin: 0  auto; width: 960px; padding: 30px 0;}
 #header table td.menu 
              { text-align: right;}
 #header table a
              { text-decoration: none; font-family: 'Oxygen', sans-serif; font-weight: 700; text-transform: uppercase; font-size: 14px; padding-top: 10px; color: #4D4D4D; margin-right: 30px; }
 #header table a:last-child 
              { margin-right: 0;}
 #header table a:hover
              { color: #C27638; border-bottom: 3px solid #C27638; }
 table.people { width: 55%%; }
 .logo img    { width: 290px; height: auto;}
 a.logo:hover { border-bottom: 0px !important; }            
 #main        { background: url('./images/bg.png') repeat;}
 #content     { margin: 0 auto; width: 960px;}
 #content-1   { margin:0 auto; float:left;   width:204px; padding: 0px 10px; }
 #content-1
 #content-2   { float:right;  width:736px; }
 #content-2-1 { float:left; width:656px; min-height: 460px; padding: 20px 40px 60px; line-height: 25px; background:white; box-shadow: 0 4px 8px 0 rgba(77, 77, 77, 0.38);}
 #content-2-2 { float:right;  width:80px; padding:10px; background:white; }
 #footer      { margin:0 auto; background:white; border-top: 3px solid #48A17E; }
 #footer-wrapper
              { width: 960px; margin: 0 auto; }
 .logos       { float: right; }
 .logos img   { width: 140px; height: auto; display: inline-block; }
 .logos img:first-child
              { height: 46px; margin-right: 10px; width: auto; } 
 .sidebar-links
              { margin: 5px 0 30px 0;}
 .sidebar-links a 
              { color: #4D4D4D; line-height: 1.7em; margin-left: 10px; font-size: 14px; }
 .sidebar-links a:hover
              { color: #48A17E;}
  h3          { font-family: 'Oxygen', sans-serif; font-weight: 700; font-size: 15px; color: #48A17E;  margin-bottom: 0px; text-transform: uppercase; }
  h2          { font-family: 'Oxygen', sans-serif; font-weight: 700; font-size: 25px; line-height: 30px; color: #C27638;  margin: 0px 0px 20px 0px;}
  #content-2-1 h3 { font-size: 18px; margin-bottom: 8px; text-transform: none; }
  a           { color: #4D4D4D; font-size: 14px; }
  a:hover     { color: #48A17E; }
  .document   { margin-bottom: 30px; font-size: 14px; line-height: 17px;}
  .document a { font-family: 'Oxygen', sans-serif; font-weight: 700; font-size: 16px; display: block; line-height: 22px; margin-bottom: 7px; color: #48A17E; text-decoration: none;}
  .document a:hover 
              { text-decoration: underline;}
  .document i { font-size: 11px; display: block; margin-bottom: 5px; }
  .document.abstract i 
              { font-size: 12px; line-height: 19px; }
  pre         { border: 1px solid #F1EFEB; background-color: #F6F4F0; overflow: auto; text-align: left; margin: 0px; padding: 15px;}
  input[type="email"]
              { border: 1px solid #dedad8;  display: block; font-family: Arial, sans-serif; font-size: 14px; height: 23px; line-height: 20px; outline: 0 none; padding: 7px 14px; width: 200px; text-align: center; }
  input[type="email"]:focus, input[type="email"]:hover 
              { border: 1px solid #48a17e; }
  input[type="submit"] 
              { background-color: #48a17e; border: 2px solid #48a17e; color: #fff; display: block; font-family: 'Oxygen',sans-serif; font-size: 13px; font-weight: 700; margin-top: 5px; outline: 0 none; padding: 8px; text-transform: uppercase; width: 230px; }
 .abstract    { text-align: center; }
 figure img
              { width: 100%%; height: auto; margin: 30px 0; }
 /* http://positioniseverything.net/easyclearing.html) */
 .cf:after { display:block; clear:both; height:0; visibility:hidden; content:" "; font-size:0; }
 /* use conditional comments for this bit if you want valid CSS */
 .cf {*zoom:1;}

 /*]]>*/
 </style>
 </style>
</head>

<body>
 <div id="body">
  <div id="header" class="cf">
   <table border="0" width="960">
	<tr>
     <td width="1" rowspan="2">
      <a href=
     "http://www.geo.uzh.ch/microsite/3dveglab/" target="_blank" class="logo"><img alt=
     "3d vegetation lab" height="90" src="http://www.geo.uzh.ch/microsite/3dveglab/software/veglablogo.png" /></a>
    </td>
    <td>
      <div class="logos">
        <img src="http://www.esa.int/esalogo/images/downloads/Digital_logo/Hi_resolution/42_digital_logo_dark_blue_HI.png" />
        <img src="http://www.uzh.ch/uzh/authoring/images/uzh_logo_e_pos_web_main.jpg" />
      </div>
    </td>
    </tr>
    <tr>
      <td class="menu">
        <a href="http://www.geo.uzh.ch/microsite/3dveglab/index.html">Project</a>
        <a href="consortium">Consortium</a>
        <a href="people">People</a>
        <a href="documents">Docs</a>
        <a href="sites">Sites</a>
        <a href="eod">EO Data</a>
        <a href="software">Software</a>
      </td>
    </tr>
   </table>
  </div>
  <div id="main" class="cf">
    <div id="content">
       <div id="content-1">
        <h3>Sensors</h3>
        <div class="sidebar-links">
          <a href=
          "https://earth.esa.int/web/guest/missions/3rd-party-missions/historical-missions/landsat-tmetm;jsessionid=20181E62B0A37B8CCD6613286FE6539F.eodisp-prod4040">LANDSAT</a><br />
          <a href=
          "https://earth.esa.int/web/guest/missions/esa-operational-eo-missions/envisat/instruments/meris">MERIS</a><br />
          <a href=
          "https://earth.esa.int/web/guest/missions/3rd-party-missions/current-missions/terraaqua-modis">MODIS</a><br />
          <a href=
          "https://earth.esa.int/web/guest/missions/esa-future-missions/sentinel-2">Sentinel
          2</a><br />
          <a href=
          "https://earth.esa.int/web/guest/missions/esa-future-missions/sentinel-3">Sentinel
          3</a><br />
        </div>

        <h3>Components</h3>
        <div class="sidebar-links">
          <a href=
          "http://www.brockmann-consult.de/cms/web/beam/">Beam</a><br />
          <a href=
          "http://www.cesbio.ups-tlse.fr/us/dart/dart_contexte.html">DART</a><br />
          <a href=
          "http://www2.geog.ucl.ac.uk/~plewis/librat/">librat</a><br />
          <a href="http://www.libradtran.org">libRadtran</a><br />
        </div>
       </div>

       <div id="content-2">
        <div id="content-2-1">
          <!-- CONTENT -->
		  %s
          <!-- END CONTENT -->
        </div>
       </div>
    </div>

  </div>
  <div id="footer" class="cf">
    <div id="footer-wrapper">
      <p>Copyright &copy;2014</p>
    </div>
   
  </div>
 </div>
</body>
</html>
'''

pageindex = '''
    <h2 class="abstract">3D Vegetation Laboratory - reference site and benchmarking tool</h2>
	<figure class="abstract">
       <img alt="3d Reconstruction" src= "http://www.geo.uzh.ch/microsite/3dveglab/graphics/stand_2.jpg" />
	</figure>

	<div class="document abstract">
        <i>Watch our video illustrating the 3d reconstruction! Download it <a href="http://www.geo.uzh.ch/microsite/3dveglab/VirtualForest.mov"> here </a></i>
     </div>
                
	<h3>Abstract</h3>
	The up-coming generation of ESA operational missions - the Sentinels -
	will enhance the capability to observe the vegetated surfaces of the
	Earth.  Nevertheless the quantitative interpretation of the Earth
	Observation (EO) signal is a challenging task because vegetation is a
	complex and dynamic medium. Effects of horizontal and vertical
	heterogeneities and asymmetrical structures of vegetation as well as
	their high temporal dynamics are often neglected in the algorithm
	development, calibration and validation procedures.  To better
	understand the scientific basis as well as the potential of future and
	upcoming missions we need detailed knowledge about the observed medium
	and the processes governing the radiative transfer. The combination of
	a realistic description of the medium in high detail together with a
	validated radiative transfer model was used to create a virtual lab mimicking
	reality which is capable to assess the potential of novel observation
	systems as well as to develop new algorithms and understand scaling
	issues from point measurements to the landscape. The advancement of
	ground based LiDAR systems provided information that contributed to
	describing and reconstructing forest stands in 3D down to the
	leaf/shoot level. Such detailed representations of the canopy
	structure and the distribution of leaves/branches within a 3D
	radiative transfer model now allow for the simulation of current and
	future missions in a controlled but realistic environment. It would
	thus offer an opportunity to test and develop dedicated applications
	to integrate EO into Earth system modeling.  The 3D-VegtationLab has
	developed a concept for land surface reference sites, which was
	demonstrated for two selected pilot super-sites as a scientific
	support tool. The tool includes a standardized and comprehensive
	multi-temporal and multi-scale benchmark dataset together with a
	scientific toolbox based on a radiative transfer model. The
	3D-Vegetation Lab provides the scientific community with a common
	benchmarking tool to develop, validate and compare biophysical EO
	products from space-borne missions with special attention to prepare
	for upcoming Sentinels.  The 3D-VegetationLab was financed by ESA's
	STSE funding scheme, and partners were University College of London
	(UK), TU Wien (AUT), CESBIO Toulouse (FR) and Netcetera (CH). The main project outcomes are described in the final report (PDF) and presentation  linked below. The main achievements of the project can be found under the tabs Sites <a href="sites">Sites</a>(3d world files), <a href="eod">EO Data</a> (multi-scale and -temporal EO data) and <a href="software">Software</a> (BEAM plugin encapsuling the RT models librat and DART).
	<h3>Important Documents</h3>
<div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegLab_FinalReport.pdf"  target="_blank">
          Final Report (PDF)</a>
     </div>
    
     <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegetationLaboratory_ProjectSummary.pdf"  target="_blank">
          Project Summary (Presentation)</a>
     </div>

'''

pageconsortium = '''
    <style type="text/css" media="screen, print, projection">
        .menu a[href*="consortium"] { color: #C27638 !important; border-bottom: 3px solid #C27638;  !important; }
    </style>
    <h2>Consortium</h2>
	<table border="0">
		 <tr>
		   <td colspan="2"><h3>Prime Contractor</h3></td>
		  </tr>
		  <tr>
		   <td><a href="http://www.geo.uzh.ch/en/units/rsl">University of Zurich - Remote Sensing Labs</a></td>
		   <td><img alt="RSL" align="left" height="40" src=
		   "http://www.geo.uzh.ch/microsite/sen4sci/img/RSL_logo.jpg" /></td>
		  </tr>
		  <tr> <td>&nbsp;</td> </tr>
		  <tr>
		   <td colspan="2"><h3>Sub-contractors</h3></td>
		  </tr>
		  <tr>
		   <td><a href="http://www.geog.ucl.ac.uk/">University College London</a></td>
		   <td><img alt="UCL" align="left" height="40" src=
		   "http://sharp.cs.ucl.ac.uk/img/ucl_logo_2.jpg" /></td>
		  </tr>
		  <tr>
		   <td><a href="http://www.cesbio.ups-tlse.fr/index_us.htm">Centre d'Etudes Spatiales de la
		   BIOsph&egrave;re</a></td>
		   <td><img alt="CESBIO" align="left" height="40" src=
		   "http://www.cesbio.ups-tlse.fr/data_all/images/logo_cesbio.png" /></td>
		  </tr>
		  <tr>
		   <td><a href="http://www.ipf.tuwien.ac.at/">Technische Universit&auml;t Wien</a></td>
		   <td><img alt="TU Wien" align="left" height="40" src=
		   "http://www.tuwien.ac.at/fileadmin/t/tuwien/downloads/cd/CD_NEU_2009/TU_Logos_2009/TU-Signet.png" /></td>
		  </tr>
<tr>
		   <td><a href="http://tu-dresden.de/die_tu_dresden/fakultaeten/fakultaet_forst_geo_und_hydrowissenschaften/fachrichtung_geowissenschaften/ipf">Technische Universit&auml;t Dresden</a></td>
		   <td><img alt="TU Dresden" align="left" height="40" src=
		   "logo_blau.png" /></td>
		  </tr>
		  <tr>
		   <td><a href="http://www.netcetera.com">Netcetera AG</a></td>
		   <td><img alt="Netcetera" align="left" height="40" src=
		   "http://netcetera.com/de/dms/images/logos/nca-logo-home.GIF" /></td>
		  </tr>
		  <tr> <td>&nbsp;</td> </tr>
		  <tr>
		   <td colspan="2"><h3>Sponsor</h3></td>
		  </tr>
		  <tr>
		   <td><a href="http://www.esa.int/Our_Activities/Observing_the_Earth">European Space Agency - Earth Observation</a></td>
		   <td><img alt="ESA" align="left" height="38" src=
		   "http://www.esa.int/esalogo/images/downloads/Digital_logo/Hi_resolution/42_digital_logo_dark_blue_HI.png" /></td>
		  </tr>
	</table>
'''

pagepeople = '''
    <style type="text/css" media="screen, print, projection">
        .menu a[href*="people"] { color: #C27638 !important; border-bottom: 3px solid #C27638;  !important; }
    </style>
     <h2>People</h2>
	 <table class="people">
      <tr> <td colspan="2"><h3>Team</h3></td> </tr>

      <tr> <td>Felix Morsdorf</td> <td>RSL</td> </tr>
      <tr> <td>Reik Leiterer</td> <td>RSL</td> </tr>
      <tr> <td>Fabian Schneider</td> <td>RSL</td> </tr>
      <tr> <td>Michael Schaepman</td> <td>RSL</td> </tr>

      <tr> <td colspan="2">&nbsp;</td> </tr>

      <tr> <td>Mathias Disney</td> <td>UCL</td> </tr>
      <tr> <td>Philip Lewis</td> <td>UCL</td> </tr>

      <tr> <td colspan="2">&nbsp;</td> </tr>

      <tr> <td>Jean-Philippe Gastellu-Etchegorry</td> <td>CESBIO</td> </tr>
      <tr> <td>Nicolas Lauret</td> <td>CESBIO</td> </tr>
      <tr> <td>Tristan Gregoire</td> <td>CESBIO</td> </tr>

      <tr> <td colspan="2">&nbsp;</td> </tr>

      <tr> <td>Norbert Pfeifer</td> <td>TU Wien</td> </tr>
      <tr> <td>Markus Hollaus</td> <td>TU Wien</td> </tr>

      <tr> <td colspan="2">&nbsp;</td> </tr>

      <tr> <td>Jason Brazile</td> <td>Netcetera Zurich</td> </tr>
      <tr> <td>Cyrill Schenkel</td> <td>Netcetera Zurich</td> </tr>

      <tr> <td colspan="2">&nbsp;</td> </tr>

      <tr> <td colspan="2"><h3>Consultants</h3></td> </tr>

      <tr> <td>Jan Clevers</td> <td>WUR</td> </tr>
      <tr> <td>Hans-Gerd Maas</td> <td>TU Dresden</td> </tr>
      <tr> <td>Anne Bienert</td> <td>TU Dresden</td> </tr>
      <tr> <td>Jean-Luc Widlowski</td> <td>IES</td> </tr>

      <tr> <td colspan="2">&nbsp;</td> </tr>

      <tr> <td colspan="2"><h3>ESA Technical Officer</h3></td> </tr>
      <tr> <td>Benjamin Koetz</td> <td>ESA-ERSIN</td> </tr>
     </table>
'''

pagedocuments = '''
    <style type="text/css" media="screen, print, projection">
        .menu a[href*="documents"] { color: #C27638 !important; border-bottom: 3px solid #C27638;  !important; }
    </style>
     <h2>Publications</h2>
     <div class="document">
     <a href="http://www.sciencedirect.com/science/article/pii/S0034425714002284"  target="_blank">Simulating imaging spectrometer data: 3D forest modeling based on LiDAR and in situ data</a>
          <i>Remote Sensing of Environment, Volume 152, September 2014, Pages 235-250</i>
          Fabian D. Schneider, Reik Leiterer, Felix Morsdorf, Jean-Philippe Gastellu-Etchegorry, Nicolas Lauret, Norbert Pfeifer, Michael E. Schaepman 
     </div>
     <div class="document">
          <a href="http://www.mdpi.com/2072-4292/5/11/5424"  target="_blank">A Practical Approach for Extracting Tree Models in Forest Environments Based on Equirectangular Projections of Terrestrial Laser Scans</a>
          <i>Remote Sensing 2013, 5(11), 5424-5448; doi:10.3390/rs5115424</i> Lothar Eysn, Norbert Pfeifer, Camillo Ressl, Markus Hollaus, Andreas Grafl and Felix Morsdorf

     </div>

     <div class="document">
          <a href=
          "https://www.schweizerbart.de/papers/pfg/detail/2013/79992/Operational_forest_structure_monitoring_using_airborne_laser_scanning"  target="_blank">

Operational forest structure monitoring using airborne laser scanning </a>
          <i>Photogrammetrie, Fernerkundung, Geoinformation, 2013, 3, 173-184</i>
          Reik Leiterer, Werner Muecke, Felix Morsdorf, Markus Hollaus, Norbert Pfeifer & Michael E. Schaepman 
          
     </div>


     <div class="document">
     <a href="http://www.sciencedirect.com/science/article/pii/S0034425713002319"  target="_blank">Radiative transfer modeling in the Earth-Atmosphere system with DART model </a>
          <i>Remote Sensing of Environment , 2013, 139, 149 - 170</i>
Elay Grau & J.-P. Gastellu-Etchegorry 
     </div>



<div class="document">
     <a href="http://www.sciencedirect.com/science/article/pii/S0034425714004568"  target="_blank">Advanced radiometry measurements and Earth science applications with the Airborne Prism Experiment (APEX) </a>
          <i>Remote Sensing of Environment , 2015, 158, 207 - 219</i>
Schaepman, M. E.; Jehle, M.; Hueni, A.; D'Odorico, P.; Damm, A.; Weyermann, J.; Schneider, F. D.; Laurent, V.; Popp, C.; Seidel, F. C.; Lenhard, K.; Gege, P.; Kuechler, C.; Brazile, J.; Kohler, P.; Vos, L. D.; Meuleman, K.; Meynart, R.; Schlaepfer, D.; Kneubuehler, M. & Itten, K. I. 
     </div>


   
     <h2>Presentation</h2>
 
     <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegetationLaboratory_ProjectSummary.pdf"  target="_blank">
          Project Summary </a>
     </div>

     <h2>Documents</h2>

      <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegLab_FinalReport.pdf"  target="_blank">
          Final Report </a>
     </div>
      <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegLab_FP.pdf"  target="_blank">
          Field Protocol </a>
     </div>
     <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegLab_EOD.pdf"  target="_blank">
          Earth Observation data sets description</a>
     </div>
     <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/documents/3DVegLab_ISD.pdf"  target="_blank">
          In-situ dataset description</a>
     </div>
'''

pagesites = '''
    <style type="text/css" media="screen, print, projection">
        .menu a[href*="sites"] { color: #C27638 !important; border-bottom: 3px solid #C27638;  !important; }
    </style>
	<h2>Site Download</h2>
	<form enctype="text/html" method="post" action="http://www.etc.ch/bin/cgiwrap/jason/registration">
	Please provide your email address so that we may keep you informed of the
	latest updates to 3D Vegetation Lab activities.<br><br>
	<input type="email" name="regemail" placeholder="E-mail" required>
	<input type="submit" value="Go to Download Page  &#9654;">
	<input type="hidden" name="cmd" value="register">
	</form>
'''

pageeod = '''
    <style type="text/css" media="screen, print, projection">
        .menu a[href*="eod"] { color: #C27638 !important; border-bottom: 3px solid #C27638;  !important; }
    </style>
	<h2>Earth Observation Data</h2>
	<figure class="abstract">
        <img alt="EO Data Scales" src= "http://www.geo.uzh.ch/microsite/3dveglab/graphics/eod_scales.png" />
	</figure>
                    
	<h3>Description</h3>
	The project gathered a large number of EO datasets of the two different sites of the project which vary in their spatial and spectral characteristics. The aim is to facilitate cross- and up-scaling using the RT models of the toolbox. A subset of the EO data (~30MB) can be downloaded using the link below. If you are interested in the full data set (>70GB), please contact the PI of the project.


      <div class="document">
          <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/eod/EOD_Laegern.zip"  target="_blank">
          Earth Observation Dataset </a>
     </div>
'''

pagesoftware = '''
    <style type="text/css" media="screen, print, projection">
        .menu a[href*="software"] { color: #C27638 !important; border-bottom: 3px solid #C27638;  !important; }
    </style>
     <h2>BEAM toolkit plugin</h2>

     <img alt="Beam 3dveglab plugin" src="http://www.geo.uzh.ch/microsite/3dveglab/graphics/vlab-screenshot.png" />

     <blockquote>
     An <a href="https://github.com/netceteragroup/esa-beam">integrated
     plugin module</a> is available for version 4.11 of the <a
     href="http://www.brockmann-consult.de/cms/web/beam/">ESA BEAM Earth
     Observation Toolbox and Development Platform</a>
     <br>
     <b>Note:</b> This software plugin is functional <i><b>technically</b>, and was tested to work with both librat and DART under Windows and UNIX environments. The use of a 64bit operating system is recommended. More details on the testing and recommendations for running the toolbox examples can be found in our           <a href=
          "http://www.geo.uzh.ch/microsite/3dveglab/software/3DVegLab_Toolbox_TestingProtocol.pdf"  target="_blank">testing protocol </a> </i>
     </blockquote>

     <h3>Binary Installation</h3>Binary installation of the 3D Vegetation
     Lab plugin is automated by a command line Java installer (details below)
     which does the following:

     <ul>
      <li>copy (or replace) the plugin jar into BEAM's
      <tt>${BEAMHOME}/beam-4.11/modules</tt></li>

      <li>first-time batch run to install into BEAM's
      <tt>${HOME}/.beam/beam-vlab/auxdata/beam-vlab</tt></li>

      <li>fetch/unpack dependent software (e.g. DART, librat, libRadtran) 
      into BEAM's <tt>${HOME}/.beam/beam-vlab/auxdata/beam-vlab</tt></li>

      <li>create command line wrappers for batch operation into BEAM's
      <tt>${BEAMHOME}/beam-4.11/bin/</tt></li>
     </ul>

     <h3>Binary Installation (windows)</h3>
      <b>Two pre-install steps:</b><br>
      1. Visit the <a href="http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&amp;what=software/beam/4.11/beam_4.11_win32_installer.exe">windows 32-bit BEAM installer page</a> and download into your <b><tt>Downloads</tt></b> folder<br> 
      2. Save our <a href="http://www.geo.uzh.ch/microsite/3dveglab/software/3DVegLabInstaller.jar">3DVegLab plugin installer jar</a> file in your <b><tt>Downloads</tt></b> folder<br>
     <pre>
rem press Windows-R to get the "run" prompt, then type "cmd" to get a shell
cd %HOMEDRIVE%%HOMEPATH%\Downloads
rem <b>Note</b>: when prompted, we suggest <b>C:\\data\\Program Files (x86)\\beam-4.11</b>
rem because 3DVeglabInstaller.jar <i>will fail if Administrator access is needed</i>
beam_4.11_win32_installer.exe
move 3DVegLabInstaller.jar "C:\\data\\Program Files (x86)\\beam-4.11\\bin"
cd /d "C:\\data\\Program Files (x86)\\beam-4.11\\bin"
..\\jre\\bin\\java -jar 3DVegLabInstaller.jar
</pre>
     <h3>Binary Installation (linux)</h3>
      <b>Two pre-install steps:</b><br>
      1. Visit the <a href="http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&amp;what=software/beam/4.11/beam_4.11_linux64_installer.sh">linux 64-bit BEAM installer page</a> and download into your <b><tt>Downloads</tt></b> folder<br> 
      2. Save our <a href="http://www.geo.uzh.ch/microsite/3dveglab/software/3DVegLabInstaller.jar">3DVegLab plugin installer jar</a> file in your <b><tt>Downloads</tt></b> folder<br>
     <pre>
cd ${HOME}/Downloads
sh beam_4.11_linux64_installer.sh
mv 3DVegLabInstaller.jar ${HOME}/beam-4.11/bin
cd ${HOME}/beam-4.11/bin
../jre/bin/java -jar 3DVegLabInstaller.jar
</pre>
     <h3>Running the toolkit</h3>
     Once you have started BEAM (<b><tt>visat</tt></b>), click <b><tt>Tools/3D Vegetation Lab Processor...</tt></b>
'''

pages = (
 ('index.html',            pageindex),
 ('consortium/index.html', pageconsortium),
 ('people/index.html',     pagepeople),
 ('documents/index.html',  pagedocuments),
 ('sites/index.html',      pagesites),
 ('eod/index.html',      pageeod),
 ('software/index.html',   pagesoftware)
)

class UTIL:
  def mkdirs(path):
    import sys
    if sys.platform.startswith('java'):
      from java.io import File
      if not File(path).isDirectory():
        if not File(path).mkdirs():
          raise RuntimeError('failed to mkdir %s' % path)
    else:
      import os
      try: 
        os.stat(path)
      except:
        os.makedirs(path)
  mkdirs = staticmethod(mkdirs)

#
# generate all of the html pages
#
for page in pages:
  (fname, pg) = page
  idx = fname.find('/') 
  if (idx > -1):
    dirs = fname[0:idx]
    UTIL.mkdirs(dirs)
  
  fp = open(fname, 'w')
  fp.write(template[1:] % (baseurl, pg[1:-1]))
  fp.close()
