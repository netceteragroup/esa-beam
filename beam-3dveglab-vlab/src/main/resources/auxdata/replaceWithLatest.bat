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

echo beaminstpath is "%beaminstpath%"

echo "Running beam to unpack 3dvlab auxdata..."
"%beaminstpath%\jre\bin\java.exe" ^
    -Xmx1024M ^
    -Dceres.context=beam ^
    "-Dbeam.mainClass=org.esa.beam.framework.processor.ProcessorRunner" ^
    "-Dbeam.processorClass=com.netcetera.vlab.VLabProcessor" ^
    "-Dbeam.home=%beaminstpath%" ^
    "-Dncsa.hdf.hdflib.HDFLibrary.hdflib=%beaminstpath%\modules\lib-hdf-2.7\lib\jhdf.dll" ^
    "-Dncsa.hdf.hdf5lib.H5.hdf5lib=%beaminstpath%\modules\lib-hdf-2.7\lib\jhdf5.dll" ^
    -jar "%beaminstpath%\bin\ceres-launcher.jar" h:\dummy.xml

set helper=%HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata\doshelper.jar
if not exist %helper% (
  echo %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata\doshelper.jar not found
  exit /b 1
)

echo "Successfully unpacked 3dvlab auxdata"
cd /d %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata

rd /q /s dummy_windows32*.*
"%beaminstpath%"\jre\bin\java -jar %helper%  fetch ftp://ftp.netcetera.ch/pub/dummy_windows32-20130103.zip
"%beaminstpath%"\jre\bin\java -jar %helper%  unzip dummy_windows32-20130103.zip
>> Versions.txt echo dummy_windows32-20130103.zip
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
