import 'dart:convert';

import 'package:http/http.dart' as http;

class NetworkHandler {
  static final client = http.Client();
  static void post(var body, String endpoint) async {
    print(body);
    try {
      var response =
          await client.post(buildUrl(endpoint), body: body, headers: {
        'Content-type': 'application/json',
        'Accept': 'application/json',
      });
      print(response.body);
    } catch (e) {
      print(e.toString());
    }
  }

  static Uri buildUrl(String endpoint) {
    String host = "http://192.168.45.236:8000/";
    final apiPath = host + endpoint;
    return Uri.parse(apiPath);
  }
}
