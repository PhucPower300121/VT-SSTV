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

## ⚠️ Known Features (Not Bugs)
- **The "Left-Edge Trap":** Don't use images with super bright left edges, unless you want that sweet analog glitch vibe!
