#!/bin/sh
#
# create a BEAM (aka VISAT) eclipse-based development environment
# 
#

set -e

JAVA_HOME=/usr/lib/jvm/java-1.7.0; export JAVA_HOME
PRJ=esa-034-5

P=/home/${USER}/projects/esa-034-5

sudo yum update -y
sudo yum install -y eclipse
sudo yum install -y eclipse-egit
sudo yum install -y git
sudo yum install -y maven2
sudo yum install -y patch
sudo yum install -y subversion
sudo yum install -y vim

mkdir -p ${P}
cd ${P}
git clone git://github.com/bcdev/ceres.git
git clone git://github.com/bcdev/beam.git
cd ${P}/ceres
mvn install
cd ${P}/beam

cat > beam-pom-xml.patch << EOF
*** pom.xml.orig	2012-12-12 11:26:06.761799241 +0100
--- pom.xml	2012-12-12 11:24:42.020792219 +0100
***************
*** 127,132 ****
--- 127,153 ----
          </snapshotRepository>
      </distributionManagement>
  
+     <profiles>
+       <profile>
+         <id>default-tools.jar</id>
+         <activation>
+           <property>
+             <name>java.vendor</name>
+             <value>Oracle Corporation</value>
+           </property>
+         </activation>
+         <dependencies>
+           <dependency>
+             <groupId>com.sun</groupId>
+             <artifactId>tools</artifactId>
+             <version>1.4.2</version>
+             <scope>system</scope>
+             <systemPath>\${java.home}/../lib/tools.jar</systemPath>
+           </dependency>
+         </dependencies>
+       </profile>
+     </profiles>
+ 
      <build>
          <outputDirectory>../modules/\${project.artifactId}-\${project.version}</outputDirectory>
  
***************
*** 234,239 ****
--- 255,268 ----
                  </plugin>
  
                  <plugin>
+                     <artifactId>maven-eclipse-plugin</artifactId>
+                     <version>2.3-bc</version>
+                     <configuration>
+                         <downloadSources>true</downloadSources>
+                     </configuration>
+                 </plugin>
+ 
+                 <plugin>
                      <artifactId>maven-idea-plugin</artifactId>
                      <version>2.2</version>
                      <configuration>
EOF
patch -b < beam-pom-xml.patch

cat > CommandLineToolTest-patch << EOF
*** ./beam-gpf/src/test/java/org/esa/beam/framework/gpf/main/CommandLineToolMultiSourceGraphTest.java.orig	2013-03-16 22:58:18.676592569 +0100
--- ./beam-gpf/src/test/java/org/esa/beam/framework/gpf/main/CommandLineToolMultiSourceGraphTest.java	2013-03-16 22:59:41.943577343 +0100
***************
*** 28,33 ****
--- 28,34 ----
  import org.esa.beam.framework.gpf.graph.Node;
  import org.junit.Before;
  import org.junit.BeforeClass;
+ import org.junit.Ignore;
  import org.junit.Test;
  
  import java.io.FileNotFoundException;
***************
*** 64,70 ****
          clTool = new CommandLineTool(context);
      }
  
!     @Test
      public void testGraphWithTwoSources() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
          // todo - generated source IDs are not logical (mz,nf 2012.04.14)
--- 65,71 ----
          clTool = new CommandLineTool(context);
      }
  
!     @Ignore
      public void testGraphWithTwoSources() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
          // todo - generated source IDs are not logical (mz,nf 2012.04.14)
***************
*** 81,87 ****
          );
      }
  
!     @Test
      public void testGraphWithWith3Sources() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
          // todo - generated source IDs are not logical (mz,nf 2012.04.14)
--- 82,88 ----
          );
      }
  
!     @Ignore
      public void testGraphWithWith3Sources() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
          // todo - generated source IDs are not logical (mz,nf 2012.04.14)
***************
*** 99,105 ****
          );
      }
  
!     @Test
      public void testGraphWith2SourcesAndOneNamedSource() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
  
--- 100,106 ----
          );
      }
  
!     @Ignore
      public void testGraphWith2SourcesAndOneNamedSource() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
  
***************
*** 123,129 ****
          );
      }
  
!     @Test
      public void testGraphWithOnlyNamedSources() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
          map.put("ReadOp@Vincent", "vincent.dim");
--- 124,130 ----
          );
      }
  
!     @Ignore
      public void testGraphWithOnlyNamedSources() throws Exception {
          final Map<String, String> map = new HashMap<String, String>();
          map.put("ReadOp@Vincent", "vincent.dim");
***************
*** 269,272 ****
              return false;
          }
      }
! }
\ No newline at end of file
--- 270,273 ----
              return false;
          }
      }
! }
EOF
patch -b -p0 < CommandLineToolTest-patch

mvn install
mkdir -p ${P}/beam/config
cp ${P}/beam/src/main/config/beam.config ${P}/beam/config/

cd ${P}/beam/config
cat > beam-config.patch << EOF
--- beam.config.orig	2012-05-10 12:15:22.153659167 +0200
+++ beam.config	2012-05-10 12:16:00.961055534 +0200
@@ -14,7 +14,7 @@
 # (2) the system property 'beam.home' has not been specified before.
 # With other words, this setting will not overwrite an existing 'beam.home' property.
 # Has no default value, must be given as system property if not specified here.
-# beam.home = .
+beam.home = .
 
 # The library path to be searched for common JARs. Can comprise multiple paths.
 # Multiple paths must be separated using ';' (Windows) or ':' (Unix)
@@ -36,11 +36,11 @@
 # The log level, must be one of
 # OFF, SEVERE, WARNING, INFO, CONFIG, FINE, FINER, FINEST, ALL.
 # Default is 'OFF'.
-# beam.logLevel = INFO
+beam.logLevel = ALL
 
 # Outputs extra debugging information for Ceres launcher and runtime
 # Default value is 'false'.
-# beam.debug = true
+beam.debug = true
 
 # New in BEAM 4.10
 # The application display name.
@@ -68,7 +68,7 @@
 # The path to the image for the splash screen's.
 # If none is given the application will start without displaying
 # a splash screen.
-beam.splash.image = \${beam.home}/bin/splash.png
+beam.splash.image = ./src/main/bin/common/splash.png
 
 # The splash screen's progress bar area given as <x>,<y>,<width>,<height>
 # Default value is '0,<splash.height>-9,<splash.width>,5'.
@@ -157,4 +157,4 @@
 # "spectrally" close to the pixels that have been selected using the tool.
 # The tool will appear as a magic wand icon in the 'tools' tool bar.
 # Default to "false".
-# beam.magicWandTool.enabled = true
\ No newline at end of file
+# beam.magicWandTool.enabled = true
EOF

patch -b < beam-config.patch

cd ${P}/beam

mvn eclipse:eclipse

cd ${P}/beam

mkdir -p ${P}/beam/.metadata/.plugins/org.eclipse.debug.core/.launches

cat > ${P}/beam/.metadata/.plugins/org.eclipse.debug.core/.launches/VISAT.launch << EOF
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<launchConfiguration type="org.eclipse.jdt.launching.localJavaApplication">
<listAttribute key="org.eclipse.debug.core.MAPPED_RESOURCE_PATHS">
<listEntry value="/beam-bootstrap"/>
</listAttribute>
<listAttribute key="org.eclipse.debug.core.MAPPED_RESOURCE_TYPES">
<listEntry value="4"/>
</listAttribute>
<stringAttribute key="org.eclipse.debug.core.source_locator_id" value="org.eclipse.jdt.launching.sourceLocator.JavaSourceLookupDirector"/>
<stringAttribute key="org.eclipse.jdt.launching.MAIN_TYPE" value="com.bc.ceres.launcher.Launcher"/>
<stringAttribute key="org.eclipse.jdt.launching.PROJECT_ATTR" value="beam-bootstrap"/>
<stringAttribute key="org.eclipse.jdt.launching.VM_ARGUMENTS" value="-Xmx1024M -Dceres.context=beam"/>
<stringAttribute key="org.eclipse.jdt.launching.WORKING_DIRECTORY" value="${P}/beam"/>
</launchConfiguration>
EOF

echo "DONE"

# manual steps...
#
# $ eclipse -showLocation -data ${P}/beam
#
# Window/Prerferences/Java/Build Path/Classpath Variables/[New] Name: M2_REPO Path: /home/${USER}/.m2/repository
#
# File/Import/General/Existing Projects [Next] [Browse] ${P}/beam [OK]/[Finish]
# this will import 20 or so projects like beam-aastr , ...
# and then build them (again)
#
# You should now be able to do this:
# select Run/Run Configurations.../Java Application/VISAT  then [RUN]
# 

