# Push Controller

Ableton Live controller interface built with Kivy.

## Features

- **Clip View**: Session view with clip triggering and mixer controls
- **Devices View**: Parameter control with 8 encoders and pagination  
- **Note View**: Melodic and drum modes with scale-aware pads
- **Settings View**: MIDI channel and OSC configuration

## Installation

### Raspberry Pi (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url> push_controller
   cd push_controller
   ```

2. **Run the installation script:**
   ```bash
   chmod +x install_rpi.sh
   ./install_rpi.sh
   ```

3. **Run the application:**
   ```bash
   source venv/bin/activate
   python3 main.py
   ```

### Manual Installation

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv libsdl2-dev
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Development Setup

```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage
```bash
python3 main.py
```

### Raspberry Pi Optimized
```bash
python3 run_rpi.py  # If available
```

### Auto-start on Boot
```bash
sudo systemctl enable push-controller.service
```

## Configuration

- **MIDI Channel**: Configure in Settings View (1-16)
- **OSC Settings**: Set IP address and port in Settings View
- **Display**: 800x480 optimized for 7" displays

## Architecture

```
├── main.py              # Application entry point
├── config/              # Configuration files
├── logic/               # Business logic and state management
├── ui/                  # User interface components
│   ├── screens/         # Main application screens
│   └── widgets/         # Reusable UI components
└── assets/              # Icons and resources
```

## Hardware Requirements

- **Raspberry Pi 4** (recommended)
- **7" Display** (800x480)
- **USB MIDI Controller** (optional)
- **Network connection** for OSC

## License

MIT License
