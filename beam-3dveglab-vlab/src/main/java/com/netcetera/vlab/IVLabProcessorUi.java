/*
 * Copyright (C) 2010-2013 Netcetera Switzerland (info@netcetera.com)
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

import java.util.Vector;
import javax.swing.JComponent;
import org.esa.beam.framework.processor.Request;

public interface IVLabProcessorUi {
    public JComponent      getGuiComponent()            throws Exception;
    public void            setRequests(Vector requests) throws Exception;
    public void            setDefaultRequests()         throws Exception;
    public Vector<Request> getRequests()                throws Exception;
    public void            setDefaultRequest()          throws Exception;
}
