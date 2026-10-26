# Android app wrapper (optional)

The main project is already installable as a Progressive Web App (PWA) on Android after HTTPS deployment. That is the simplest path and does not require publishing an APK.

If you need a native Android wrapper later:
1. Install Node.js LTS and Android Studio with Android SDK.
2. Deploy this Flask server to a public HTTPS domain (do not use `127.0.0.1` as the backend address on a phone).
3. Create a Capacitor project using the official Capacitor documentation: https://capacitorjs.com/docs
4. Point the Android app's start URL / web content to your deployed SureSight HTTPS website, or build a packaged frontend and configure its API base URL to the backend.
5. Run the project through Android Studio, test on a real device, and configure app signing before creating a release APK/AAB.

A signed APK/AAB is not included in this starter. The website and PWA can be run now with the root setup instructions.
