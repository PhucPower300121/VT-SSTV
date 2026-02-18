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
<br>
<img width="250" height="184" alt="images" src="https://github.com/user-attachments/assets/2f308346-325c-4f82-a577-2ff67837b7fe" />
<img width="320" height="256" alt="export" src="https://github.com/user-attachments/assets/e4693c3b-5626-42b2-9e25-da963f0da541" />

## ⚠️ Known Features (Not Bugs)
- **The "Left-Edge Trap":** Don't use images with super bright left edges, unless you want that sweet analog glitch vibe!
- **Decoding capability when using a microphone with low volume**: Please do not use with low-volume audio sources; the algorithm will malfunction and ruin your image.

## 🤝 Call for Contributors
I built this core with **Martin M1** as a solid foundation. 
If you are a radio enthusiast or a Python wizard, feel free to:
- Add support for **Scottie S1/S2**, **Robot 36/72**, etc.
- Optimize the **Hilbert Transform** for even better noise reduction.
- Improve signal gain handling: The current engine struggles with low-volume microphones, often leading to corrupted images. We need a more robust way to normalize audio input before decoding.
- Fix the **Left-Edge Trap** once and for all!

Let's make VT-SSTV the best cross-platform SSTV tool together.

****Special Note****: The source code contains Vietnamese comments—think of it as a "Easter Egg" or an invitation to learn a bit of our language while you code! 🇻🇳
