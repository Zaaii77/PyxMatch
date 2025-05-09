# PyxMatch

Pyx is an advanced Python application that combines screen capture, image recognition, and media management functionalities. It provides a user-friendly interface for interacting with these features and includes real-time notifications and error handling.

![PyxMatch Screenshot](cpt.ico)

## Features

### 1. **User Authentication**
- Secure login system using the `keyauth` API.
- Supports user registration, login, and license upgrades.

### 2. **Screen Capture**
- Capture screenshots of specific screens using the `mss` library.
- Automatically saves screenshots in a temporary folder.

### 3. **Image Recognition**
- Compares captured screenshots with reference images using OpenCV.
- Calculates a match percentage to identify similarities.

### 4. **Media Display**
- Displays matched media (images or videos) in full-screen mode.
- Media is displayed when the match percentage exceeds the threshold set by the user in the `config.json` file.
- Supports various media formats, including `.png`, `.jpg`, `.mp4`, etc.

### 5. **Statistics Tracking**
- Logs match percentages and media usage statistics in text files.
- Organizes logs by date for easy tracking.

### 6. **Real-Time Notifications**
- Sends notifications via Telegram for:
  - Application startup.
  - Errors encountered during execution.

### 7. **Error Handling**
- Captures and logs errors.
- Sends error details to a Telegram chat for quick debugging.

### 8. **Customizable Settings**
- Loads configuration from a `config.json` file.
- Allows customization of thresholds and other parameters.

## Prerequisites

1. **Authentication Service**:
   - The application requires an authentication service to manage user login and registration.
   - By default, the code uses [KeyAuth](https://keyauth.cc/) as the authentication provider.
   - You need to configure your KeyAuth credentials (`name`, `ownerid`, `secret`, and `version`) in the code.

2. **Telegram Bot**:
   - A Telegram bot is required for sending notifications.
   - Replace `INSERT_YOUR_BOT_TOKEN` and `INSERT_YOUR_CHAT_ID` in the code with your Telegram bot token and chat ID.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Zaaii77/PyxMatch.git
   cd PyxMatch
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Telegram bot:
   - Replace `INSERT_YOUR_BOT_TOKEN` and `INSERT_YOUR_CHAT_ID` in the code with your Telegram bot token and chat ID.

4. Run the application:
   ```bash
   python PyxMatch.py
   ```

## Usage

1. **Login**:
   - Enter your username and password to log in.
   - If you don't have an account, register using the provided options.

2. **Screen Selection**:
   - Select the screen you want to capture from the dropdown menu.

3. **Start Capture**:
   - Click the "Start" button to begin capturing screenshots and analyzing them.

4. **View Media**:
   - Matched media will be displayed automatically in full-screen mode when the match percentage exceeds the threshold set in `config.json`.

5. **Access Logs**:
   - Check the `logs` folder for match percentages and media usage statistics.

## Dependencies

- Python 3.8+
- PyQt5
- Tkinter
- OpenCV
- MSS
- Requests
- Pillow
- Screeninfo

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or support, please contact [lowatell@student.s19.be].
