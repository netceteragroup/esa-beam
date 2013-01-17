@echo off
setlocal

cd /d %HOMEDRIVE%
echo Searching %HOMEDRIVE% for beam installation...
call :findbeam

if "%beaminstpath%" == "" (
  echo Error: beam installation not found on %HOMEDRIVE%
  echo Failed
  exit /b 1
) 

echo Using beaminstpath = "%beaminstpath%"

echo Creating 3dveglab dummy input file: %TEMP%\dummy.xml

 > %TEMP%\dummy.xml echo ^<?xml version="1.0" encoding="ISO-8859-1"?^>
>> %TEMP%\dummy.xml echo ^<RequestList^>
>> %TEMP%\dummy.xml echo    ^<Request type="VLAB"^>
>> %TEMP%\dummy.xml echo        ^<Parameter name="3dScene" value="Default RAMI" /^>
>> %TEMP%\dummy.xml echo        ^<OutputProduct file="vlab_out.dim" format="BEAM-DIMAP" /^>
>> %TEMP%\dummy.xml echo    ^</Request^>
>> %TEMP%\dummy.xml echo ^</RequestList^>

if exist %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab (
  echo Removing existing beam-vlab...
  echo PRESS CONTROL-C WITHIN 10 SECONDS TO CANCEL!
  ping 1.1.1.1 -n 1 -w 10000 > nul 2>&1
  rd /q /s %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab 
)

echo Running beam to unpack 3dveglab auxdata...

"%beaminstpath%\jre\bin\java.exe" ^
    -Xmx1024M ^
    -Dceres.context=beam ^
    "-Dbeam.mainClass=org.esa.beam.framework.processor.ProcessorRunner" ^
    "-Dbeam.processorClass=com.netcetera.vlab.VLabProcessor" ^
    "-Dbeam.home=%beaminstpath%" ^
    "-Dncsa.hdf.hdflib.HDFLibrary.hdflib=%beaminstpath%\modules\lib-hdf-2.7\lib\jhdf.dll" ^
    "-Dncsa.hdf.hdf5lib.H5.hdf5lib=%beaminstpath%\modules\lib-hdf-2.7\lib\jhdf5.dll" ^
    -jar "%beaminstpath%\bin\ceres-launcher.jar" %TEMP%\dummy.xml > nul 2>&1

set helper=%HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata\doshelper.jar
if not exist %helper% (
  echo %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata\doshelper.jar not found
  exit /b 1
)

echo Successfully unpacked 3dvlab auxdata
cd /d %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata

echo Removing existing dummy_windows32 (if any)...
rd /q /s dummy_windows32*.* > nul 2>&1
echo Fetching binaries for "dummy"...
"%beaminstpath%"\jre\bin\java -jar %helper%  fetch ftp://ftp.netcetera.ch/pub/dummy_windows32-20130103.zip
echo Unpacking binaries for "dummy"...
"%beaminstpath%"\jre\bin\java -jar %helper%  unzip dummy_windows32-20130103.zip
echo Registering version for "dummy"...
>> Versions.txt echo dummy_windows32-20130103.zip
echo Cleaning up...
rename dummy_windows32-20130103 dummy_windows32
del dummy_windows32-20130103.zip
goto :done

:findbeam
for /f "usebackq tokens=*" %%a in (`dir /s/b \*beam-4.10.3`) do (
  if exist %%a set beaminstpath=%%a
  exit /b
)

:done
echo Successfully completed
endlocal
exit /b 0
