[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![AGPL License][license-shield]][license-url]

<h1 align="center">Cue Splitter</h1>

<p align="center">
  A web-based tool to split audio albums using CUE sheets into individual track files with format conversion support
  <br />
  <br />
  <a href="https://github.com/L-a-s-s-y/Cue-Splitter">View Demo</a>
  ·
  <a href="https://github.com/L-a-s-s-y/Cue-Splitter/issues">Report Bug</a>
  ·
  <a href="https://github.com/L-a-s-s-y/Cue-Splitter/issues">Request Feature</a>
</p>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#features">Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#docker-deployment">Docker Deployment</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#supported-formats">Supported Formats</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

**Cue Splitter** is a web-based application that allows you to split audio albums stored as single files with CUE sheets into individual track files. Built with Flask and powered by [FFcuesplitter](https://github.com/jeanslack/FFcuesplitter), it provides an easy-to-use web interface for converting entire albums into separate songs while preserving metadata and offering various output format options.

Perfect for music enthusiasts who have audio albums in formats like FLAC with CUE sheets and want to convert them into individual track files for better organization and compatibility with music players.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

This project is built with the following technologies:

* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
* ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
* ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
* ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
* ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Features

- **Web-based Interface**: Simple HTML upload form for easy file management
- **Multiple Audio Format Support**: Process FLAC, APE, MP3, WAV, OGG, and WV files
- **Format Conversion**: Convert output to FLAC, MP3, WAV, OGG, or Opus
- **Metadata Preservation**: Maintains album information, track titles, and audio properties
- **Flexible Output Options**: Customizable compression levels, sample rates, and quality settings
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Automatic Cleanup**: Built-in file management and cleanup scripts

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Ensure you have the following installed on your machine:

**For Manual Installation:**
- **Python**: Version 3.8 or higher
  - [Download Python](https://www.python.org/downloads/)
- **FFmpeg**: Required for audio processing
  - [Install FFmpeg](https://ffmpeg.org/download.html)

**For Docker Deployment:**
- **Docker**: Version 20.10 or higher
  - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Version 2.0 or higher
  - [Install Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/L-a-s-s-y/Cue-Splitter.git
   ```

2. Navigate to the project directory
   ```sh
   cd Cue-Splitter
   ```

3. Create and activate a virtual environment
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the required dependencies
   ```sh
   pip install -r cue-splitter/requirements.txt
   ```

5. Run the Flask application
   ```sh
   cd cue-splitter
   flask --app api run --host=0.0.0.0
   ```

The application will be available at `http://localhost:5000`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Docker Deployment

For production deployment, Docker is the recommended approach:

1. **Clone the repository**
   ```sh
   git clone https://github.com/L-a-s-s-y/Cue-Splitter.git
   cd Cue-Splitter
   ```

2. **Build and start the services**
   ```sh
   docker-compose up -d --build
   ```

The application will be available at `http://localhost:80`

**Docker Configuration:**
- The application runs behind an Nginx reverse proxy
- Gunicorn serves the Flask application with 4 workers
- Local cue-splitter directory mounted for code access
- Automatic container restart policy enabled

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

1. **Access the Web Interface**: Navigate to the application URL in your browser
2. **Upload Files**: 
   - Select your CUE file (`.cue` format)
   - Select the corresponding audio file (FLAC, APE, MP3, WAV, OGG, or WV)
3. **Review Album Information**: The application will display:
   - Album title, artist, and release date
   - Track listings
   - Audio format details (codec, sample rate, channels)
4. **Configure Output Settings**:
   - Choose output format (FLAC, MP3, WAV, OGG, Opus, or copy original)
   - Adjust quality settings and compression levels
   - Set sample rate and format preferences
5. **Download Results**: The split tracks will be packaged into a ZIP file for download

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Supported Formats

### Input Audio Formats
- **FLAC** (`.flac`) - Free Lossless Audio Codec
- **APE** (`.ape`) - Monkey's Audio
- **MP3** (`.mp3`) - MPEG Audio Layer III
- **WAV** (`.wav`) - Waveform Audio File Format
- **OGG** (`.ogg`) - Ogg Vorbis
- **WV** (`.wv`) - WavPack

### Output Audio Formats
- **FLAC** - With customizable compression levels (0-8)
- **MP3** - With bitrate options (128k, 192k, 256k, 320k)
- **WAV** - PCM format with various sample rates
- **OGG** - Vorbis with quality and bitrate settings
- **Opus** - Modern audio codec for efficient compression
- **Copy** - Preserve original format and quality

### CUE Sheet Support
- Standard CUE sheet format (`.cue`)
- Automatic encoding detection and normalization
- Metadata extraction (album, artist, date, genre, catalog)
- Track title and timing information

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Configuration

### Environment Variables

The Docker deployment supports the following environment variables:

```yaml
environment:
  - CUE_GUNICORN_WORKERS=4        # Number of Gunicorn worker processes
  - CUE_API_TIMEOUT=300           # Request timeout in seconds
```

### Volume Mounts

```yaml
volumes:
  - ./cue-splitter:/cue-splitter  # Mount local cue-splitter directory
```

### Nginx Configuration

The application includes a pre-configured Nginx setup with:
- Large file upload support (5000M limit)
- Extended timeouts for long processing operations
- CORS headers for cross-origin requests
- Proper proxy headers for Flask integration

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the GNU Affero General Public License v3.0. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Project Link: [https://github.com/L-a-s-s-y/Cue-Splitter](https://github.com/L-a-s-s-y/Cue-Splitter)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/L-a-s-s-y/Cue-Splitter.svg?style=for-the-badge
[contributors-url]: https://github.com/L-a-s-s-y/Cue-Splitter/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/L-a-s-s-y/Cue-Splitter.svg?style=for-the-badge
[forks-url]: https://github.com/L-a-s-s-y/Cue-Splitter/network/members
[stars-shield]: https://img.shields.io/github/stars/L-a-s-s-y/Cue-Splitter.svg?style=for-the-badge
[stars-url]: https://github.com/L-a-s-s-y/Cue-Splitter/stargazers
[issues-shield]: https://img.shields.io/github/issues/L-a-s-s-y/Cue-Splitter.svg?style=for-the-badge
[issues-url]: https://github.com/L-a-s-s-y/Cue-Splitter/issues
[license-shield]: https://img.shields.io/github/license/L-a-s-s-y/Cue-Splitter.svg?style=for-the-badge
[license-url]: https://github.com/L-a-s-s-y/Cue-Splitter/blob/main/LICENSE