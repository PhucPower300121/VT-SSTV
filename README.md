# VT-SSTV
VT-SSTV is a modern implementation of Slow Scan Television (SSTV) for transmitting and receiving images over radio frequencies.

VT-SSTV is a modern implementation of Slow Scan Television (SSTV) for transmitting and receiving images over radio frequencies.

## ⚙ Features:

• Transmit images with Martin M1 SSTV mode

• Receive SSTV signals in real-time or from WAV files

• Support for call sign overlay

• Audio sample rate auto-detection

• Dark mode UI for comfortable usage

## 🚀 Installation
- With Python3
  1. Install dependencies: `pip install numpy sounddevice pysstv Pillow scipy`
  2. Run the magic: `python SSTV.py`
- With .exe file
  1. Download from release page
  2. enjoy it!

## 📡 Supported Protocol
- **Martin M1 Only:** This version is fine-tuned specifically for Martin M1. 
- **Why?** Because it balances quality and speed perfectly (the sweet 1m55s spot).
- *Other modes (Scottie, Robot) are not supported in v3.9.*

## 🖥 Screenshots
<img width="602" height="682" alt="image" src="https://github.com/user-attachments/assets/417690e5-cbe7-401d-9a35-11c12aa921d3" />
<img width="602" height="682" alt="image" src="https://github.com/user-attachments/assets/800c2748-1732-41c3-989c-062d27b39c57" />
<img width="602" height="682" alt="image" src="https://github.com/user-attachments/assets/096e9227-8911-489f-a8ef-03637806d911" />
![images](https://github.com/user-attachments/assets/dfcd8178-9509-4223-8a35-5a6c83fdc38f)
<img width="320" height="256" alt="export" src="https://github.com/user-attachments/assets/e4693c3b-5626-42b2-9e25-da963f0da541" />

## ⚠️ Known Features (Not Bugs)
- **The "Left-Edge Trap":** Don't use images with super bright left edges, unless you want that sweet analog glitch vibe!
