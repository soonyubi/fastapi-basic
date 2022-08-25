import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:login_tutorial/login/controller/login_controller.dart';

class RegisterPage extends StatelessWidget {
  RegisterPage({Key? key}) : super(key: key);
  var loginController = Get.put(LoginController());
  @override
  Widget build(BuildContext context) {
    final emailCtrl = TextEditingController();
    final pwdCtrl = TextEditingController();

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 30),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('register'),
            const SizedBox(height: 40),
            TextField(
              controller: loginController.emailTextEditCtrl,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'email',
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: loginController.pwdTextEditCtrl,
              obscureText: true,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'password',
              ),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () {
                    loginController.login();
                  },
                  child: Text('submit'),
                ),
                ElevatedButton(
                  onPressed: () {},
                  child: Text('go to login page'),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
