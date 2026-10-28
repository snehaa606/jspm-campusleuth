# 📱 JSPM CampuSleuth Android Mobile App

This directory contains the **Native Android Studio App** source code for **JSPM CampuSleuth**.

---

## 🌟 Key Native App Features
* **Full-Screen Native Experience:** Standalone app view without any browser address bar.
* **Camera & File Chooser Integration:** Take snapshots of found items directly inside the app.
* **Direct WhatsApp Intent Handling:** Clicking "Share to WhatsApp" or the Daily Bulletin opens the real native WhatsApp app seamlessly!
* **Pull-to-Refresh:** Swipe down to reload live lost & found feeds.
* **Hardware Back Button Handling:** Navigates back inside app history instead of quitting.

---

## 🛠️ How to Open & Build APK in Android Studio

1. Open **Android Studio**.
2. Click **Open** and select the `android_app` folder (`c:\Users\Sneha Patil\Downloads\Sneha\android_app`).
3. Let Gradle sync dependencies.
4. **Build APK:**
   * Go to **Build** menu > **Build Bundle(s) / APK(s)** > **Build APK(s)**.
   * Locate the generated `.apk` in `app/build/outputs/apk/debug/app-debug.apk`.
5. Install and run on any Android phone or Emulator!

> 💡 **Note on Localhost URL:**  
> When testing on an Android Emulator, the app connects to `http://10.0.2.2:5000/`.  
> When testing on a real physical Android phone connected to the same Wi-Fi, change `APP_URL` in `MainActivity.java` to your computer's local IP (e.g. `http://192.168.1.5:5000/`).
