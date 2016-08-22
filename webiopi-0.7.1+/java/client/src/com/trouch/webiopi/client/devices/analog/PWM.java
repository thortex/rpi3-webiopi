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

public class PWM extends DAC {

	public PWM(PiClient client, String deviceName) {
		super(client, deviceName, "pwm");
	}

	public float readAngle(int channel) {
		return Float.parseFloat(this.sendRequest("GET", "/" + channel + "/angle"));
	}

	public float writeAngle(int channel, float angle) {
		return Float.parseFloat(this.sendRequest("POST", "/" + channel + "/angle/" + angle));
	}

}
