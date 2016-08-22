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

package com.trouch.webiopi.client.devices.analog;

import com.trouch.webiopi.client.PiClient;

public class DAC extends ADC {

	public DAC(PiClient client, String deviceName) {
		super(client, deviceName);
	}

	public DAC(PiClient client, String deviceName, String type) {
		super(client, deviceName, type);
	}

	public float writeFloat(int channel, float value) {
		return Float.parseFloat(this.sendRequest("POST", "/" + channel + "/float/" + value));
	}

	public float writeVolt(int channel, float value) {
		return Float.parseFloat(this.sendRequest("POST", "/" + channel + "/volt/" + value));
	}

}
