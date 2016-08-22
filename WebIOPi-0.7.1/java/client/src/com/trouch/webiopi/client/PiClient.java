/* Copyright 2013 Eric Ptak - trouch.com
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
*/

package com.trouch.webiopi.client;

import org.apache.commons.codec.binary.Base64;

public abstract class PiClient {
	
	protected String urlBase;
	protected String auth;

	public static String encodeCredentials(String login, String password) {
		return Base64.encodeBase64String((login + ":" + password).getBytes());
	}

	public PiClient(String protocol, String host, int port) {
		this.urlBase = protocol + "://" + host + ":" + port; 
	}
	
	public void setCredentials(String login, String password) {
		this.auth = "Basic " + encodeCredentials(login, password);
	}
	
	public abstract String sendRequest(String method, String path) throws Exception;

}
