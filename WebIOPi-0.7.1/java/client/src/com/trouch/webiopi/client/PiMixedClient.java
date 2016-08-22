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

public class PiMixedClient extends PiClient {
	private PiHttpClient http;
	private PiCoapClient coap;
	
	private int tries 	 = 0;
	private int maxTries = 3;
	
	public PiMixedClient(String host) {
		super("", "", 0);
		http = new PiHttpClient(host);
		coap = new PiCoapClient(host);
	}
	
	public PiMixedClient(String host, int httpPort, int coapPort) {
		super("", "", 0);
		http = new PiHttpClient(host, httpPort);
		coap = new PiCoapClient(host, coapPort);
	}
	
	@Override
	public void setCredentials(String login, String password) {
		http.setCredentials(login, password);
		coap.setCredentials(login, password);
	}

	@Override
	public String sendRequest(String method, String path) throws Exception {
		if (tries < maxTries) {
			String response = coap.sendRequest(method, path);
			if (response != null) {
				tries = 0;
				return response;
			}
			tries++;
		}
		
		return http.sendRequest(method, path);
	}
	
}
