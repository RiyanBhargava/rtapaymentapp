# RTA Multi-Modal Payment Scanner

A web application for Dubai's Roads and Transport Authority (RTA) that handles payments for multi-modal transportation including taxi, bus, and metro services.

## Features

- 🤖 **AI-Powered Journey Analysis**: Uses ByteDance AI to parse journey details
- 🚗🚇🚌 **Multi-Modal Support**: Handles taxi, metro, bus, and walking transfers
- 💳 **QR Code Payment System**: Generates QR codes for each transport mode
- ✅ **Visual Feedback**: Shows tick animation after successful payments
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🎯 **Step-by-Step Journey**: Guides users through each transport mode

## Installation

1. **Clone or download the project**
   ```bash
   cd rta_payment_scanner
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your ByteDance API key:
   ```
   BYTEPLUS_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   - Navigate to `http://localhost:5000`

## Usage

### 1. Enter Journey Details

Paste your journey information in this format:

```
=== Detailed Journey with Lines/Bus Numbers ===
1. taxi: 1 stop, 8.5 min, 4.2 km
   Stops: Dubai Marina Walk -> Mall of the Emirates Metro Station

2. transfer (walk): 2 stops, 1.0 min, 0.02 km
   Stops: Mall of the Emirates Metro Station entrance -> Mall of the Emirates Metro Station 1

3. MRed1 (metro): 7 stops, 12.1 min, 15.8 km
   Stops: Mall of the Emirates Metro Station 1 -> Union Metro Station 2

4. transfer (walk): 3 stops, 2.0 min, 0.05 km
   Stops: Union Metro Station 2 -> Union Metro Station (Green Line) -> Union Bus Terminal

5. 64 (bus): 8 stops, 18.3 min, 12.4 km
   Stops: Union Bus Terminal -> Gold Souq Bus Station -> Ras Al Khor Industrial Area
```

### 2. Analyze Journey

Click "Analyze Journey & Calculate Fare" to process the journey using AI and calculate total fares.

### 3. Generate QR Codes

Click "Generate QR Code" to start the payment process:

- **Taxi**: Single QR code for complete payment
- **Metro/Bus**: Two QR codes (entrance and exit)
- **Transfers**: No payment required

### 4. Scan QR Codes

Use "Simulate QR Scan" button to demo the scanning process:

- Shows tick animation after successful scan
- Automatically progresses to next transport mode
- Displays "Journey Completed" when finished

## Project Structure

```
rta_payment_scanner/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── templates/           # HTML templates
│   ├── index.html       # Home page with journey input
│   ├── qr_code.html     # QR code display page
│   ├── exit_qr.html     # Exit QR code for metro/bus
│   └── journey_complete.html # Journey completion page
├── static/              # Static files
│   └── tick_video.mp4   # Success animation video
└── README.md           # This file
```

## API Integration

The app uses ByteDance's Ark API for intelligent journey parsing:

```python
from byteplussdkarkruntime import Ark

client = Ark(
    base_url="https://ark.ap-southeast-1.bytepluses.com/api/v3",
    api_key="your-api-key"
)

response = client.chat.completions.create(
    model="seed-1-6-250615",
    messages=[...]
)
```

## Fare Calculation

- **Taxi**: Minimum 12 AED + 8 AED per km
- **Metro**: 3 AED base + 0.5 AED per km  
- **Bus**: 2 AED base + 0.3 AED per km
- **Walking Transfers**: Free

## QR Code Flow

1. **Initial QR**: Generated for first transport mode
2. **Entry QR**: For metro/bus entrance (shows tick animation)
3. **Exit QR**: For metro/bus exit (completes payment)
4. **Next Mode**: Automatically moves to next transport
5. **Completion**: Shows success screen when journey ends

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Configuration

The application uses environment variables for secure configuration:

- Copy `.env.example` to `.env` 
- Set your ByteDance API credentials
- Modify fare rates in `config.py` if needed
- Add/remove Dubai transport stops in `config.py`

**Important**: Never commit your `.env` file with actual API keys to version control!

## Security

- API keys are stored in environment variables (`.env` file)
- Session management for user journey tracking
- QR codes contain encrypted payment information
- HTTPS recommended for production deployment

## Troubleshooting

**Common Issues:**

1. **API Key Error**: Ensure your ByteDance API key is valid and properly set in `.env`
2. **Environment Variables**: Make sure `.env` file exists and `python-dotenv` is installed
3. **Video Not Playing**: Check that `tick_video.mp4` is in the `static/` directory
4. **Session Issues**: Clear browser cookies if experiencing session problems
5. **QR Code Not Generating**: Verify the `qrcode` and `Pillow` libraries are installed

## License

This project is developed for Dubai RTA hackathon/competition purposes.

## Support

For questions or issues, please check the documentation or create an issue in the project repository.

---

**Note**: This application is designed for demonstration purposes. In production, implement proper security measures, error handling, and payment processing integration.
