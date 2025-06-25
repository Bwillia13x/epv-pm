# EPV Research Platform

The EPV Research Platform is an autonomous research tool that uses Bruce Greenwald's methodology to perform intrinsic value calculations and earnings power value analysis for stocks. It offers features like comprehensive company analysis, data collection, intrinsic value calculations, and a web-based dashboard.

## Features

- Earnings Power Value (EPV) analysis
- Comprehensive financial statement analysis
- Quality assessment
- Peer comparisons
- Risk analysis
- Investment recommendations
- Web-based dashboard

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Analyze a stock:

```bash
python src/main.py analyze --symbol AAPL --peers MSFT,GOOGL --years 10 --export json
```

Quick EPV calculation:

```bash
python src/main.py quick --symbol AAPL
```

Batch analysis:

```bash
python src/main.py batch --symbols AAPL,MSFT,GOOGL
```

Start the web interface:

```bash
python src/main.py web --port 8050
```

### Web Interface

Access the web interface at `http://127.0.0.1:8050` after starting the server.

## Configuration

- All configuration settings are in `config/config.py`.
- Set environment variables or use `.env` for sensitive information like API keys.

## Directory Structure

- **src**: Source code
  - **config**: Configuration files
  - **data**: Data collection and integration modules
  - **analysis**: Analysis and calculation modules
  - **models**: Data models
  - **ui**: Web interface
  - **utils**: Utility scripts

## License

This project is licensed under the MIT License.
