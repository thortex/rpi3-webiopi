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

package com.trouch.webiopi.client.devices;

import com.trouch.webiopi.client.PiClient;

public class Device {
	
	private PiClient client;
	protected String path;

	public Device(PiClient client, String deviceName, String type) {
		this.client = client;
		if (type != null) {
			this.path = "/devices/" + deviceName + "/" + type;
		}
		else {
			this.path = "/devices/" + deviceName;
		}
	}
	
	public String sendRequest(String method, String subPath) {
		try {
			return this.client.sendRequest(method, this.path + subPath);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
	}

}
