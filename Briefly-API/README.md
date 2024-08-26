# Briefly-API

The Briefly-API offers a variety of endpoints for managing modes, fetching news, summarizing content, formatting text, handling topics, and managing users. Below is a streamlined guide to understanding the API and getting started.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Summary](#api-summary)
- [Contributing](#contributing)


## Installation

Set up the project locally:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/dvolynov/Fryends-API
   cd Fryends-API

2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   Create a `.env` file in the root of your project and add your environment-specific settings (e.g., database credentials, API keys).

5. **Run database migrations:**
   Ensure your database is set up and run any necessary migrations.

## Usage

Run the application using:
```sh
uvicorn main:app --reload
```

## API Summary

- `Modes` - manage and update the operational mode (text or audio) for different chat sessions.
- `News` - retrieve news content tailored to specific chat sessions.
- `Summaries` - generate summaries from text, files, URLs, or audio inputs.
- `Text Formats` - customize and fetch text formatting options for various chat sessions.
- `Topics` - set and retrieve preferred topics for individual chat sessions.
- `Users` - manage user information, including adding new users and checking user existence.


## Contributing

Contributions are welcome! Please follow the guidelines outlined in the repository.
