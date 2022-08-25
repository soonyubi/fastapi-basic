import 'package:flutter/widgets.dart';
import 'package:get/get.dart';
import 'package:login_tutorial/login/model/login_model.dart';
import 'package:login_tutorial/service/network_handler.dart';

class LoginController extends GetxController {
  TextEditingController emailTextEditCtrl = TextEditingController();
  TextEditingController pwdTextEditCtrl = TextEditingController();
  void login() {
    LoginModel loginModel = LoginModel(
        email: emailTextEditCtrl.text, password: pwdTextEditCtrl.text);
    // print(loginModel.toJson());
    // print(loginModelToJson(loginModel));
    NetworkHandler.post(loginModelToJson(loginModel), 'users');
  }
}
