/*
 * Copyright (C) 2010-2014 Netcetera Switzerland (info@netcetera.com)
 * 
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, see http://www.gnu.org/licenses/
 *
 * @(#) $Id: $
 */

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.PrintWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FilenameFilter;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.Thread;
import java.math.BigInteger;
import java.net.JarURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.channels.Channels;
import java.nio.channels.ReadableByteChannel;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.util.Enumeration;
import java.util.jar.Attributes;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Scanner;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class Install {
  private static final String TYPE_BIN         = "bin";
  private static final String TYPE_MODULES     = "modules";
  private static final String TYPE_AUX         = "aux";
  private static final String TYPE_LIB         = "lib";
  private static final String DEFAULT_REPO     = "ftp://ftp.netcetera.ch/pub";
  private static final String DEFAULT_MANIFEST = DEFAULT_REPO + "/3DVegLab.manifest";
  
  public static void die(String msg) {System.err.println(msg); System.exit(1);}
  public static void fetch(String urlName, String targetName) throws Exception {
      System.out.println("fetch " + urlName + " " + targetName);
      URL url                 = null;
      ReadableByteChannel rbc = null;
      while (rbc == null) {
        try {
          url = new URL(urlName);
          rbc = Channels.newChannel(url.openStream());
        } catch (Exception e) {
          // might be trying to fetch from a busy server - sleep and retry
          System.out.println("got " + e.getMessage() + "\ngc, sleep, and retry...");
          url = null;
          rbc = null;
          // without calling gc(), this seems to loop forever
          System.gc();
          Thread.sleep(4000);
        }
      }
      FileOutputStream fos    = new FileOutputStream(targetName);
      long nbytes = fos.getChannel().transferFrom(rbc, 0, Long.MAX_VALUE);
      fos.close();
      System.out.println(nbytes + " bytes downloaded");
  }
  public static String md5sum(String fName) throws Exception {
    System.out.println("md5sum " + fName);
    MessageDigest md = MessageDigest.getInstance("MD5");
    InputStream   is = new FileInputStream(fName);
    try {
      byte[] buf = new byte[64 * 1024];
      is = new DigestInputStream(is, md); while (is.read(buf) != -1);
    }
    finally {is.close();}
    return String.format("%1$032x", new BigInteger(1,md.digest()));
  }
  public static void unzip(String baseDir, String zipPath) throws Exception {
    System.out.println("unzip " + baseDir + " " + zipPath);
    Enumeration<?> entries; ZipFile zipFile;
    zipFile = new ZipFile(zipPath); entries = zipFile.entries();
    while (entries.hasMoreElements()) {
      ZipEntry ent = (ZipEntry) entries.nextElement();
      if (ent.isDirectory()) {
        (new File(baseDir, ent.getName())).mkdirs();
      } else {
        File newFile = new File(baseDir, ent.getName());
        InputStream   in = zipFile.getInputStream(ent);
        OutputStream out = new BufferedOutputStream(new FileOutputStream(newFile));
        byte[] buffer = new byte[1024]; int len;
        while ((len = in.read(buffer)) >= 0) out.write(buffer, 0, len);
        in.close(); out.close();
      }
    }
    zipFile.close();
  }

  private static File createDummyInput() throws Exception {
    File dummyInput = new File(System.getProperty("java.io.tmpdir"), "dummy.xml");
    BufferedWriter out = new BufferedWriter(new FileWriter(dummyInput));
    for (String line : new String[] {
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>",
        "<RequestList>",
        "   <Request type=\"VLAB\">",
        "     <Parameter name=\"3dScene\" value=\"Default RAMI\"/>",
        "     <OutputProduct file=\"vlab_out.dim\" format=\"BEAM-DIMAP\"/>",
        "   </Request>",
        "</RequestList>"}) {
      out.write(line + "\n");
    }
    out.close();
    return dummyInput;
  }
  private static File createRunScript(String bindir) throws Exception {
    System.out.println("Creating 3DVegLabProcessor script...");
    String fileName = null;
    String[] lines = null;
    if (System.getProperty("os.name").startsWith("Windows")) {
      fileName = "3DVegLab.bat";
      lines = new String[] { 
        "@echo off",
        "",
        "set BEAM4_HOME=" + new File(bindir, "..").getCanonicalPath(),
        "",
        "\"%BEAM4_HOME%\\jre\\bin\\java.exe\" ^",
        "    -Xmx1024M ^",
        "    -Dceres.context=beam ^",
        "    \"-Dbeam.mainClass=org.esa.beam.framework.processor.ProcessorRunner\" ^",
        "    \"-Dbeam.processorClass=com.netcetera.vlab.VLabProcessor\" ^",
        "    \"-Dbeam.home=%BEAM4_HOME%\" ^",
        "    \"-Dncsa.hdf.hdflib.HDFLibrary.hdflib=%BEAM4_HOME%\\modules\\lib-hdf-2.7\\lib\\jhdf.dll\" ^",
        "    \"-Dncsa.hdf.hdf5lib.H5.hdf5lib=%BEAM4_HOME%\\modules\\lib-hdf-2.7\\lib\\jhdf5.dll\" ^",
        "    -jar \"%BEAM4_HOME%\\bin\\ceres-launcher.jar\" %*",
        "",
        "exit /B %ERRORLEVEL%"
      };
    } else {
      fileName = "3DVegLab.sh";
      lines = new String[] { 
        "#! /bin/sh",
                                "",
        "export BEAM4_HOME=" + new File(bindir, "..").getCanonicalPath(),
        "",
        ". \"$BEAM4_HOME/bin/detect_java.sh\"",
        "",
        "\"$app_java_home/bin/java\" \\",
        "    -Xmx1024M \\",
        "    -Dceres.context=beam \\",
        "    \"-Dbeam.mainClass=org.esa.beam.framework.processor.ProcessorRunner\" \\",
        "    \"-Dbeam.processorClass=com.netcetera.vlab.VLabProcessor\" \\",
        "    \"-Dbeam.home=$BEAM4_HOME\" \\",
        "    \"-Dncsa.hdf.hdflib.HDFLibrary.hdflib=$BEAM4_HOME/modules/lib-hdf-2.7/lib/libjhdf.so\" \\",
        "    \"-Dncsa.hdf.hdf5lib.H5.hdf5lib=$BEAM4_HOME/modules/lib-hdf-2.7/lib/libjhdf5.so\" \\",
        "    -jar \"$BEAM4_HOME/bin/ceres-launcher.jar\" \"$@\"",
        "",
        "exit $?"
      };
    }
    File runScript = new File(bindir, fileName);
    BufferedWriter out = new BufferedWriter(new FileWriter(runScript));
    for (String line : lines) {
      out.write(line + "\n");
    }
    out.close();
    runScript.setExecutable(true);
    return runScript;
  }
  private static String join(String[] args, String jstr) {
    String result = "";
    for (String s: args) {
      if (result == "") {
        result = s;
      } else {
        result = result + jstr + s;
      }
    }
    return result;
  }
  private static int run3DVegLabProcessor(File inputFile, File scriptFile) throws Exception {
    System.out.println("Running 3DVegLabProcessor...");
    String[] cmd;
    if (System.getProperty("os.name").startsWith("Windows")) {
      cmd = new String[] {"cmd", "/c", "\" \"" + scriptFile.getCanonicalPath() + "\" \"" + inputFile.getCanonicalPath() + "\" 2>&1 \""};
    } else {
      cmd = new String[] {"sh", "-c", scriptFile.getCanonicalPath() + " " + inputFile.getCanonicalPath()  + " 2>&1"};
    }
    System.out.println("Executing: " + join(cmd, " "));
    ProcessBuilder pb = new ProcessBuilder(cmd);
    Process proc = pb.start();   
    // hack - collect but ignore output
    new Scanner( proc.getInputStream() ).useDelimiter("\\Z").next();
    return proc.waitFor();
  }
  private static boolean recursiveDelete(File path) {
    if (path.exists()) {
      File[] files = path.listFiles();
      for (int i = 0; i < files.length; i++) {
        if (files[i].isDirectory()) {
          recursiveDelete(files[i]);
        } else {
          files[i].delete();
        }
      }
    }
    return (path.delete());
  }

  /**
   * This method should be call to correctly install DART in the 3DVegLab plugin
   *
   * @param DARTfor3DVegLab: Path to the DARTfor3DVegLab.jar file that should be 
   *                         run to install correctly DART in the 3DVegLab plugin.
   * @param args: A list of String arguments that should be passed to DARTfor3DVegLab.jar.
   *              This JAR needs two arguments:
   *               - DART_FOLDER: The DART folder where was extracted the archive (hopefully
   *                 this is the same where the DARTfor3DVegLab.jar file is located).
   *               - DART_LOCAL: The location where the DART_LOCAL variable should point out.
   *                 In DART this variable should point out the folder that contains the
   *                 simulation folder.
   */
  private static void runDARTinstaller(String DARTfor3DVegLab, String[] args)
    throws MalformedURLException, IOException {
    // Load URL from String argument
    URL url = new URL("file:" + DARTfor3DVegLab);
    // Init the URLClassLoader
    URLClassLoader URLcl = new URLClassLoader(new URL[] {url});

    // Get MainClass name
    URL JARurl = new URL("jar", "", url + "!/");
    JarURLConnection JARuc = (JarURLConnection)JARurl.openConnection();
    Attributes attribut = JARuc.getMainAttributes();
    String mainClassName = attribut != null ? attribut.getValue(Attributes.Name.MAIN_CLASS) : null;

    // Invokes class
    try {
      // Instanciate the class and get the method
      Class<?> klass = URLcl.loadClass(mainClassName);
      Method mainMethod = klass.getMethod("main", new Class[] {args.getClass()});
      mainMethod.setAccessible(true);
      int modifiers = mainMethod.getModifiers();

      // Check the 'main'
      if (mainMethod.getReturnType() != void.class || ! Modifier.isStatic(modifiers) ||
            ! Modifier.isPublic(modifiers)) {
        throw new NoSuchMethodException("main");
      }
      try {
        // Launch the main method from DARTfor3DVegLab
        mainMethod.invoke(null, new Object[] { args });
      } catch (IllegalAccessException e) {
    }
    } catch (Exception e) {
      e.printStackTrace();
      System.exit(-1);
    }
  }

  private static void makePathsInLibratSceneFilesAbsolute(File dir) throws IOException {
    for (File fileOrDir : dir.listFiles())
      if (fileOrDir.isDirectory())
        makePathsInLibratSceneFilesAbsolute(fileOrDir);
      else if (fileOrDir.getName().matches("^[a-zA-Z0-9\\-_\\.]+(.obj|.obj.crown|.dem)$"))
        makePathsInFileAbsolute(fileOrDir);
  }

  private static void makePathsInFileAbsolute(File destination) throws IOException {
    File source = makeBackupFile(destination);
    destination.createNewFile();
    BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(source), "UTF-8"));
    PrintWriter writer = new PrintWriter(new OutputStreamWriter(new FileOutputStream(destination), "UTF-8"));
    String lineBuffer = null;
    while ((lineBuffer = reader.readLine()) != null)
      writer.println(makePathInStringAbsolute(lineBuffer, destination.getParentFile()));
    reader.close();
    writer.close();
  }

  private static String makePathInStringAbsolute(String string, File dir) {
    return string.replaceAll("\\./", dir.getAbsolutePath());
  }
  
  private static File makeBackupFile(File source) {
    File destination = new File(source.getPath() + ".bak");
    source.renameTo(destination);
    return destination;
  }
  
  private static void install(String repoURL, String manifestUrl) throws Exception {
    // Get current working directory
    String cwd = new File(".").getCanonicalPath();

    // Test if we are inside beam-*/bin directory
    String endPath = "beam-4.11:bin".replaceAll(":", Matcher.quoteReplacement(File.separator));
    if (!cwd.endsWith(endPath)) {
      die("Run me from inside a directory ending with: " + endPath + " (not: " + cwd + ")");
    }

    // Set directories path
    String bindir = cwd;
    String moddir = new File(cwd, ".." + File.separator + TYPE_MODULES).getAbsolutePath();
    String libdir = new File(cwd, ".." + File.separator + TYPE_LIB).getAbsolutePath();
    String auxsuffix = ".beam:beam-vlab:auxdata".replaceAll(":", Matcher.quoteReplacement(File.separator));
    String auxdir = null;
    if (System.getProperty("os.name").startsWith("Windows")) {
      auxdir = new File(System.getenv("HOMEDRIVE")+System.getenv("HOMEPATH"), auxsuffix).getCanonicalPath();
    } else {
      auxdir = new File(System.getenv("HOME"), auxsuffix).getCanonicalPath();
    }
    File vlabaux = new File(auxdir, "..").getCanonicalFile();

    System.out.println("Clearing existing 3DVegLab auxdata: " + vlabaux);
    System.out.println("Succeeded? -> " + recursiveDelete(vlabaux));
    System.out.println("Fetching " + manifestUrl);
    
    // Get 3DVegLab.manifest file from manifestURL
    Scanner sc = new Scanner(new URL(manifestUrl).openStream());
    String text = sc.useDelimiter("\\Z").next(); sc.close();

    // Process manifest
    System.out.println("Processing " + manifestUrl);
    for (String line : text.split("\n")) {
      // Set up tuple, targetName and newBaseName
      String[] tuple = line.split(":");
      String targetName = null;
      String newBaseName = "";
      if (tuple.length > 3) {
        newBaseName = tuple[3];
      }
      if (TYPE_BIN.equals(tuple[1])) {
        targetName = bindir + File.separator + tuple[2];
      } else if (TYPE_AUX.equals(tuple[1])) {
        targetName = auxdir + File.separator + tuple[2];
      } else if (TYPE_LIB.equals(tuple[1])) {
        targetName = libdir + File.separator + tuple[2];
      } else if (TYPE_MODULES.equals(tuple[1])) {
        for (File toDelete : new File(moddir).listFiles(new FilenameFilter() {
          public boolean accept(File directory, String fileName) {
              return fileName.startsWith("beam-3dveglab-vlab");
          }})) {
          System.out.println("Deleting " + toDelete.getCanonicalPath());
          toDelete.delete();
        }
        targetName = moddir + File.separator + tuple[2];
      } else {
        die("unknown file locator: " + tuple[1]);
      }

      // Fetch targetName from repoURL
      fetch(repoURL + "/" + tuple[2], targetName);

      // Get md5sum and compare it to one from manifest
      String cksum = md5sum(targetName);
      if (!cksum.equals(tuple[0])) {
        die("md5sum mismatch: expected=" + tuple[0] + " actual=" + cksum);
      }

      // Get oldPath and newPath to rename if necessary
      String oldPath = null;
      String newPath = null;
      for ( String ext : new String[] {".zip", ".tar.gz"} ) {
        if (targetName.endsWith(ext)) {
          oldPath = targetName.substring(0, targetName.length()-ext.length());
          newPath = deriveName(oldPath, newBaseName);
        }
      }

      // Test type (modules, zip and tar.gz)
      if (TYPE_MODULES.equals(tuple[1])) {
        // modules
        File script = createRunScript(bindir);
        File dummy  = createDummyInput();
        run3DVegLabProcessor(dummy, script);
        if (! new File(auxdir).isDirectory()) {
          die("no auxdir - running 3DVegLab must have failed");
        }
      } else if (targetName.endsWith(".zip")) {
        // ZIP archive
        // Unzip and delete fetched targetName file
        unzip(new File(targetName, "..").getCanonicalPath(), targetName);
        System.out.println("Deleting " + targetName);
        new File(targetName).delete();

        // If manifest point out a new base, move targetName to newBaseName
        if (!newBaseName.equals("")) {
          System.out.println("Renaming " + oldPath + " to " + newPath);
          new File(oldPath).renameTo(new File(newPath));
        }
      } else if (targetName.endsWith(".tar.gz")) {
        // tar.gz archive
        // Check the running OS is not Windows
        if (! System.getProperty("os.name").startsWith("Windows")) {
          // Create and run command line to extract .tar.gz archive
          String [] cmd = new String[] {"sh", "-c", "tar -C " + new File(targetName, "..").getCanonicalPath() + " -xzvf " + targetName};
          System.out.println("Running " + join(cmd, " "));
          ProcessBuilder pb = new ProcessBuilder(cmd);
          Process proc = pb.start();
          // hack - collect but ignore output
          new Scanner( proc.getInputStream() ).useDelimiter("\\Z").next();
          proc.waitFor();

          // Delete targetName
          System.out.println("Deleting " + targetName);
          new File(targetName).delete();

          // If manifest point out a new base, move targetName to newBaseName
          if (!newBaseName.equals("")) {
            System.out.println("Renaming " + oldPath + " to " + newPath);
            new File(oldPath).renameTo(new File(newPath));
          }
        }
      }

      File target = new File(targetName);
      String targetFilename = target.getName();
      
      if (targetFilename.startsWith("librat_scenes")) makePathsInLibratSceneFilesAbsolute(target.getParentFile());

      // Test if targetName is a DART archive
      if (targetFilename.startsWith("DART")
          && !(System.getProperty("os.name").startsWith("Windows") ^ targetName.endsWith(".zip"))) {
        // Get DART directory
        String DARTfolder = newPath;

        // Get DARTfor3DVegLab.jar path
        String DARTfor3DVegLab = newPath + File.separator + "DARTfor3DVegLab.jar";

        // Create arguments array that will be passed to DARTfor3DVegLab.jar
        String[] args = new String[2];
        args[0] = DARTfolder;
        // /!\ WARNING /!\ Keep this variable up to date and consistent with the dart_scene*.zip
        args[1] = new File(DARTfolder).getParent() + File.separator + "dart_local";

        // run DART installer
        System.out.println("Running DART installer");
        runDARTinstaller(DARTfor3DVegLab, args);
      }

    }
    System.out.println("Successfully completed.");
  }
  private static String deriveName(String oldName, String newBaseName) throws Exception {
    String newName = "";
    String[] comps = oldName.split(Matcher.quoteReplacement(File.separator));
    String basename = comps[comps.length-1];
    if (newBaseName.length() > 0) {
      newName = new File(oldName, "..").getCanonicalPath() + File.separator + newBaseName;
    } else {
      newName = new File(oldName, "..").getCanonicalPath() + File.separator + basename;
    }
    return newName;
  }
  public static void main(String[] args) throws Exception {
    switch (args.length){
      case 0:
        install(DEFAULT_REPO, DEFAULT_MANIFEST);
        break;
      case 2:
      case 3:
        if ("fetch".compareTo(args[0]) == 0) {
          String urlName         = args[1];
          String targetName      = null;
          String[] parts         = urlName.split(";type=");
          String[] components    = parts[0].split("/");
          targetName             = components[components.length - 1];
          if (args.length == 3) { targetName = args[2]; }
          fetch(urlName, targetName);
        } else if ("unzip".compareTo(args[0]) == 0) {
          if(args.length != 2) { die("unzip expects unzipPath"); }
          unzip(new File(".").getCanonicalPath(), args[1]);
        } else if ("repo".compareTo(args[0]) == 0) {
          if(args.length != 3) { die("repo expects repoURL manifestURL"); }
          install(args[1], args[2]);
        } else {
          die("unknown subcommand: " + args[0]); 
        }
        break;
      default:
        die("Invalid arguments");
        break;
    }
  }
}
