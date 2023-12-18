import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCMk-jWD8RgFoFQSvMfDrjP25qmPwiQK0Q",
  authDomain: "yumyumdelivery-12ebb.firebaseapp.com",
  projectId: "yumyumdelivery-12ebb",
  storageBucket: "yumyumdelivery-12ebb.appspot.com",
  messagingSenderId: "772726972796",
  appId: "1:772726972796:web:0eb1ae51194aee6b7204f9"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);


// Initialize Firebase Authentication and get a reference to the service
const auth = getAuth(app);
