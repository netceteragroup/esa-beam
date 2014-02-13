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

import com.netcetera.vlab.IVLabProcessorUi;
import com.netcetera.vlab.VLabJythonFactory;
import com.netcetera.vlab.VLabProcessor;

import org.esa.beam.framework.param.ParamGroup;
import org.esa.beam.framework.param.Parameter;
import org.esa.beam.framework.processor.ProcessorException;
import org.esa.beam.framework.processor.ui.AbstractProcessorUI;
import org.esa.beam.framework.processor.ui.ProcessorApp;
import org.esa.beam.util.Guardian;
import javax.swing.JComponent;
import java.awt.Rectangle;
import java.io.File;
import java.util.Vector;
import java.util.logging.Logger;

public class VLabUi extends AbstractProcessorUI {
	private static final String JYTHON_UI_ICLASSNAME      = "com.netcetera.vlab.IVLabProcessorUi";
	private static final String JYTHON_IMPL_CLASSNAME     = "VLabImpl";
	private static final String JYTHON_UI_IMPL_CLASSNAME  = "VLabUiImpl";
	private        final Logger _logger                   = Logger.getLogger("beam.processor.vlab");
    public static IVLabProcessorUi delegate;
    private Parameter _paramOutputProduct;
    private static int window_width;
    private static int window_height;

    public VLabUi() {
        _logger.info("instantiating VLabUi delegate...");
        delegate = (IVLabProcessorUi) VLabJythonFactory.getJythonObject(JYTHON_UI_ICLASSNAME,
		    new File(VLabProcessor.auxdataInstallDir, JYTHON_IMPL_CLASSNAME + ".py").getAbsolutePath(), 
		    JYTHON_UI_IMPL_CLASSNAME);
    }

    @Override
    public JComponent getGuiComponent() {
    	JComponent guiComponent;
    	try {
    		guiComponent = delegate.getGuiComponent();
    	} catch (Exception e) {
    		throw new RuntimeException("getGuiComponent failed!", e);
    	}
        requestWindowSize();
        return guiComponent;
    }

    @Override public Vector getRequests()        throws ProcessorException {
    	Vector requests = null;
    	try {
    		requests = delegate.getRequests();
    	} catch (Exception e) {
    		throw new ProcessorException("getRequests failed!", e);
    	}
    	return requests;
    }
    @Override public void   setDefaultRequests() throws ProcessorException {
    	try {
    		delegate.setDefaultRequests();
    	} catch (Exception e) {
    		throw new ProcessorException("setDefaultRequests failed!", e);
    	}
    }

    @Override
    public void setRequests(Vector requests)     throws ProcessorException {
        Guardian.assertNotNull("requests", requests);
        try {
        	delegate.setRequests(requests);
        } catch (Exception e) {
        	throw new ProcessorException("setRequests failed!", e);
        }
    }
 
    @Override
    public void setApp(ProcessorApp app) {
        super.setApp(app);
        final ParamGroup paramGroup = new ParamGroup();
        paramGroup.addParameter(_paramOutputProduct);
        app.markIODirChanges(paramGroup);
    }
    
    public static void setWindowSize(int width, int height){ window_width = width; window_height = height; }
    
    public void requestWindowSize(){
        getApp().getMainFrame().getDockingManager().setInitBounds(new Rectangle(0, 0, window_width, window_height));
    }
}
