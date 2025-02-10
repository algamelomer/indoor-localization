### 📍 Indoor Localization with ESP32 and Flask

This project implements an **indoor localization system** using **ESP32 microcontrollers** and a **Flask server**. The goal is to achieve accurate position tracking within a home-scale environment, using **WiFi signal strength** for localization.

## 🚀 Features
- **ESP32-based Localization:** Three fixed ESP32 devices form a triangular reference network, while a fourth mobile ESP32 estimates its position.
- **Flask Server:** Collects WiFi signal data and computes the real-time position of the mobile ESP32.
- **Real-Time Visualization:** Displays fixed ESP32 devices as **blue dots** and the mobile ESP32 as a **red dot**.
- **Scalable & Customizable:** Can be extended with more nodes for improved accuracy.

## 📌 How It Works
1. **Setup ESP32 Nodes:**
   - Three fixed ESP32 devices broadcast their WiFi signal.
   - A fourth mobile ESP32 scans available networks and sends its data to the server.
   
2. **Localization Algorithm:**
   - The Flask server receives WiFi signal strengths from the mobile ESP32.
   - Using triangulation or machine learning, the system estimates the mobile ESP32's position.

3. **Visualization:**
   - A web-based or GUI visualization tool displays the ESP32 positions in real-time.

## 📂 Project Structure
```
indoor-localization/
│── esp32/            # Code for ESP32 devices
│── server/           # Flask backend for processing data
│── visualization/    # Real-time visualization of ESP32 positions
│── README.md         # Project documentation
```

## 🔧 Installation & Usage
1. **Flash ESP32 Code:** Upload the appropriate firmware to each ESP32.
2. **Run Flask Server:**  
   ```bash
   cd server
   python app.py
   ```
3. **Visualize Results:** Open the visualization tool to see real-time tracking.

## 📌 Future Enhancements
- **More Accurate Localization Algorithms:** Improve precision with advanced signal processing.
- **Integration with AI:** Use machine learning for better position estimation.
- **Web Dashboard:** Build a user-friendly interface for real-time monitoring.

## 👨‍💻 Author
Developed by **Omar Algamel**  
[GitHub Profile](https://github.com/algamelomer)  
