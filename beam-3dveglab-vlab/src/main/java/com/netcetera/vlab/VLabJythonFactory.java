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

package com.netcetera.vlab;

import java.io.File;
import java.io.IOException;
import java.util.logging.Logger;

import org.python.core.PySystemState;
import org.python.util.PythonInterpreter;

public class VLabJythonFactory {
    private static VLabJythonFactory instance    = null;
    private static PythonInterpreter interpreter = null;
    private static final String VLAB_LOGGERID    = "beam.processor.vlab";
    
    public synchronized static VLabJythonFactory getInstance() {
        if (instance == null) { instance = new VLabJythonFactory(); }
        return instance;
    }
    
    public synchronized static PythonInterpreter getInterpreter(String jyFilePath) {
        if (interpreter == null) {
        	String jyCanPath  = null;
        	File jyFile       = new File(jyFilePath);
			PySystemState sys = new PySystemState();
			sys.setClassLoader(VLabJythonFactory.getInstance().getClass().getClassLoader());
			interpreter       = new PythonInterpreter(null, sys);
			try {
				jyCanPath     = jyFile.getCanonicalPath();
			} catch (IOException ex) {
				throw new RuntimeException("getCanonicalPath failed for ["+jyFile+"]",ex);
			}
			Logger.getLogger(VLAB_LOGGERID).info("Loading vlab code from: [" + jyCanPath + "]");
            interpreter.execfile(jyCanPath);
        }
    	return interpreter;
    }

    public static Object getJythonObject(String iFaceName, String jyFilePath, String jyClassName ) {
        Object javaIface     = null;
		String instanceName  = jyClassName.toLowerCase();
		String javaClassName = jyClassName.substring(0, 1).toUpperCase()+jyClassName.substring(1);
		String codeToEval    = String.format("%s=%s()", instanceName, javaClassName);
		Logger.getLogger(VLAB_LOGGERID).info("Eval()ing jython implementation: [" + codeToEval + "]");
		getInterpreter(jyFilePath).exec(codeToEval);
		Logger.getLogger(VLAB_LOGGERID).info("Resolving java interface reference ["+iFaceName+"]");
        try {
            Class<?> JavaInterface = Class.forName(iFaceName);
            Logger.getLogger(VLAB_LOGGERID).info("Obtaining instantiated jython object ["+jyClassName+"]");
            javaIface = interpreter.get(instanceName, JavaInterface);
            Logger.getLogger(VLAB_LOGGERID).info("jython delegate [" + jyClassName + "] ready for service");
        } catch (Exception ex) {
            throw new RuntimeException("jython delegate could not be instantiated: ", ex);
        }
        return javaIface;
    }
}
