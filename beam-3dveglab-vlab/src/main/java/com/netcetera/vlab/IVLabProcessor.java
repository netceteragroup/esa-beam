/*
 * Copyright (C) 2010-2015 Netcetera Switzerland (info@netcetera.com)
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
 */

package com.netcetera.vlab;

import org.esa.beam.framework.processor.Request;
import com.bc.ceres.core.ProgressMonitor;

public interface IVLabProcessor {
    public void process(ProgressMonitor pm, Request request) throws Exception;
    public String getUITitle();
    public String getName();
    public String getSymbolicName();
    public String getVersion();
    public String getCopyrightInformation();
    public String getLoggerName();
}
