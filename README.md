# URL Shortener with FastAPI

This project is a simple URL shortener API that allows users to shorten URLs, retrieve original URLs, update URLs, delete URLs, and get statistics on the number of accesses. It also includes a basic HTML frontend built using Tailwind CSS to shorten URLs.


## Overview

This project uses FastAPI to create a URL shortening service. The backend interacts with a MongoDB database to store the original URL and the corresponding shortened URL, along with the number of accesses.

The API provides several features, including:

* URL shortening
* Redirecting to the original URL
* URL updates
* Deleting URLs
* Access statistics

## Requirements

* Python 3.7+
* FastAPI
* Uvicorn (ASGI server)
* Motor (MongoDB async driver)
* MongoDB (local or cloud-based)
* Tailwind CSS (for the frontend styling)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/husnaingujjar170/husnain-innovaxelAssessment.git
cd url-shortener
```

### 2. Create a virtual environment (optional, but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Note**: You will need to install MongoDB locally or use a cloud service like MongoDB Atlas.

### 4. Set up environment variables

Set up a `.env` file or use your system's environment to configure the MongoDB URI:

```bash
MONGO_URI=mongodb://localhost:27017
```

### 5. Run the application

Run the application using Uvicorn:

```bash
uvicorn main:app --reload
```

This will start the FastAPI backend and make it available at `http://127.0.0.1:8000`.

## Usage

Once the application is running, you can use the API endpoints or open the frontend in your browser.

### API Endpoints

#### Create a Short URL

**POST** `/api/urls`

* **Request body**:

  ```json
  {
    "original_url": "https://www.example.com"
  }
  ```

* **Response**:

  ```json
  {
    "short_code": "abcd1234",
    "original_url": "https://www.example.com",
    "created_at": "2025-07-16T00:00:00",
    "access_count": 0,
    "access_times": []
  }
  ```

#### Redirect to Original URL

**GET** `/{short_code}`

* **Redirects** the user to the original URL associated with the short code.

#### Update a Short URL

**PUT** `/api/urls/{short_code}`

* **Request body**:

  ```json
  {
    "original_url": "https://www.updated-url.com"
  }
  ```

* **Response**:

  ```json
  {
    "short_code": "abcd1234",
    "original_url": "https://www.updated-url.com",
    "created_at": "2025-07-16T00:00:00",
    "access_count": 0,
    "access_times": []
  }
  ```

#### Delete a Short URL

**DELETE** `/api/urls/{short_code}`

* **Response**: HTTP status `204 No Content` if the URL was successfully deleted, or `404 Not Found` if the short code does not exist.

#### Get URL Statistics

**GET** `/api/urls/{short_code}/stats`

* **Response**:

  ```json
  {
    "short_code": "abcd1234",
    "original_url": "https://www.example.com",
    "created_at": "2025-07-16T00:00:00",
    "access_count": 5,
    "access_times": ["2025-07-16T00:00:00", "2025-07-16T01:00:00"]
  }
  ```

## Frontend

The frontend is a simple HTML page styled using Tailwind CSS. The page allows users to input a URL, shorten it, and view the resulting shortened URL and its access statistics.

* The frontend communicates with the `/api/urls` endpoint to shorten URLs.
* After shortening a URL, the short URL is displayed, along with the original URL, access count, and access times.

### Frontend Functionality

* **Input URL**: The user inputs a URL in the text box.
* **Shorten URL**: After clicking the "Shorten URL" button, the frontend sends the input URL to the backend and displays the shortened URL along with additional information.
* **Display Result**: After the API returns a response, the frontend displays the short URL, original URL, and access statistics.

