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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class PiHttpClient extends PiClient {
	public final static int DEFAULT_PORT = 8000;

	public PiHttpClient(String host) {
		super("http", host, DEFAULT_PORT);
	}

	public PiHttpClient(String host, int port) {
		super("http", host, port);
	}

	@Override
	public String sendRequest(String method, String path) throws Exception {
		BufferedReader reader = null;
		try {
			URL url = new URL(this.urlBase + path);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			connection.setRequestMethod(method);
			if (this.auth != null) {
				connection.setRequestProperty("Authorization", this.auth);
			}

			// read the output from the server
			reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			StringBuilder stringBuilder = new StringBuilder();

			String line = null;
			while ((line = reader.readLine()) != null) {
				stringBuilder.append(line).append('\n');
			}
			return stringBuilder.toString();
		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		} finally {
			if (reader != null) {
				try {
					reader.close();
				} catch (IOException ioe) {
					ioe.printStackTrace();
				}
			}
		}
	}

}
