This uses the subplot S2 instead of S1, because it is a denser part of
the forest with very few coniferous trees, which is generally better
modeled by our approach ( and more representative for the Laegeren
forest ). 
�
I included the 3d models as well, in order to have the complete
scene. If you don't need the 3d trunk and branch models, you can
delete the folder OBJ and replace the file "object_3d.xml" by the
corresponding file in the folder "NO_3D_OBJECTS".
�
The parameters that are interesting for you are:
�
directions.xml
- numberOfPropagationDirections="100"
- sunViewingZenithAngle="27.1" sunViewingAzimuthAngle="32.6"
- directionZenithalAngle="5.75" directionAzimuthalAngle="207.2"
- DefineOmega omega="0.0010"
�
maket.xml
- CellDimensions z="1.0" x="1.0"
- fileName="DEM.mp#"
- exactlyPeriodicScene="2"
�
phase.xml
- sensorPlaneprojection="0"
- projection="1"
- image="1"
�
DefineOmega means that you can define a solid angle of the output in
steradian. exactlyPeriodicScene="2" stands for the option infinite
slope, which means that rays leaving the scene can reenter the scene
whereas the slope is considered continuous. Other options are
isolated scene or repetitive scene. projection="1" means that an
orthorectified image is created.
�
I attached an example of a sequence file for the Landsat sensor.

These files should be compatible with DART 5.4.3, but I would recommend
using version 5.4.4 when it gets released.

Fabian Schneider

