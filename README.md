# AI-Powered Database Query Assistant (DbTalk)

## Project Description:
The AI-Powered Database Query Assistant is a microservice-based system designed to simplify employee interaction with the company database using natural language queries. The backend, developed with FastAPI and LangChain, leverages Redis for efficient caching and prompt memory. The frontend, built with React, offers a user-friendly interface for seamless interaction. A robust query validation mechanism ensures the accuracy and compliance of database operations, safeguarding data integrity. The system employs Azure’s vector database to optimize data retrieval, delivering fast and precise responses. Deployed in a scalable, containerized microservices architecture using Docker Compose, the platform is designed for efficient, streamlined operations. This innovative tool empowers employees with intuitive, efficient access to organizational data, enhancing productivity and decision-making.


## Getting Started:
### Prerequisites

Before you start, ensure you have the following installed:

- **Git** – for cloning the repository. You can download it from [here](https://git-scm.com/downloads).
- **Docker** – for running the application. You can download Docker from [here](https://www.docker.com/get-started).

## Step 1: Clone the Repository

To download the project, open your terminal or command prompt and run the following command to clone the repository from GitHub:

```bash
git clone https://github.com/arseniy-sandalov/mys_llm.git
```

## Step 2: Navigate to the Project Directory

Once the repository is cloned, navigate to the project directory by running:

```bash
cd mys_llm
```

## Step 3: Run app using Docker Compose

### 1. Running the Full-Stack Application (Frontend and Backend)
The project is configured to run both the frontend and backend services using Docker Compose. To start the full-stack application (frontend + backend + Redis), simply run:

```bash
docker-compose up --build
```
This will build and start both the frontend and backend containers. The frontend will be available on http://localhost:3000 and the backend will be available on http://localhost:8000


### 2. Running Only the Backend Service
If you only want to run the backend and Redis without the frontend, there is a separate Docker Compose file that you can use. To start only the backend, use the following commands:

```bash
docker-compose -f docker-compose.backend.yml up --build
```

This will only start the backend and Redis services. The backend will be available on http://localhost:8000.


# API Documentation

## Endpoints

### 1. User Registration
**POST** `/register`

**Description:** Registers a new user with a username and password. The username must be unique.

#### Request Body:

```json
{
    "username": "string",
    "password": "string"
}
```

- **username:** The username for the new user (string, required).
- **password:** The password for the new user (string, required).

#### Responses:

- **201 Created:**

    ```json
    {
        "message": "User registered successfully"
    }
    ```

- **400 Bad Request:**

    ```json
    {
        "detail": "Username already registered"
    }
    ```

- **500 Internal Server Error:**

    ```json
    {
        "detail": "Database error while creating user"
    }
    ```

#### Example Request

```bash
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "password": "testpassword"}'
```

---

### 2. User Login and Token Generation
**POST** `/token`

**Description:** Authenticates a user and generates a JWT access token.

#### Request Body:

```json
{
    "username": "string",
    "password": "string"
}
```

This follows the `OAuth2PasswordRequestForm` structure.

#### Responses:

- **200 OK:**

    ```json
    {
        "access_token": "string",
        "token_type": "bearer",
        "user_id": "integer"
    }
    ```

- **401 Unauthorized:**

    ```json
    {
        "detail": "Incorrect username or password"
    }
    ```

- **500 Internal Server Error:**

    ```json
    {
        "detail": "Error during login: <error_message>"
    }
    ```

#### Example Request

```bash
curl -X POST "http://localhost:8000/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=testpassword"
```

---

### 3. Token Verification
**GET** `/verify-token/{token}`

**Description:** Verifies if the provided JWT token is valid.

#### Path Parameters:

- **token:** The JWT token to be verified.

#### Responses:

- **200 OK:**

    ```json
    {
        "message": "Token is valid"
    }
    ```

- **403 Forbidden:**

    ```json
    {
        "detail": "Token is invalid or expired"
    }
    ```

- **500 Internal Server Error:**

    ```json
    {
        "detail": "Error verifying token: <error_message>"
    }
    ```

#### Example Request

```bash
curl -X GET "http://<localhost:8000>/verify-token/<your_jwt_token>"
```

---

## Connecting to the API

### 1. Establishing a Connection

To connect to the API, use HTTP requests to the respective endpoints listed above. Ensure to handle headers and request bodies as specified.

### 2. Authentication Flow

1. Register a new user using the `/register` endpoint.
2. Log in with the registered user credentials using the `/token` endpoint to receive a JWT access token.
3. Use the JWT token to access protected resources or verify the token using `/verify-token/{token}`.

---

## WebSocket Connection

### Endpoint

**URL:** `/chat/{user_id}`  
**Method:** WebSocket  
**Description:** Establish a WebSocket connection for real-time communication.

#### Path Parameter

- **user_id (string):** A unique identifier for the user. This should be generated and managed by your application.

#### Query Parameter

- **token (string):** A token used for user authentication. Ensure that the token is valid before attempting to connect.

### Connection Steps

1. **Open a WebSocket Connection:** Use the following JavaScript code to connect to the WebSocket:

    ```javascript
    const userId = 'your_user_id';
    const token = 'your_auth_token';
    const socket = new WebSocket(`ws://localhost:8000/chat/${userId}?token=${token}`);

    socket.onopen = () => {
        console.log('Connected to the WebSocket server');
    };

    socket.onmessage = (event) => {
        const response = event.data;
        console.log('Received response:', response);
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed');
    };
    ```

2. **Send a Query:** Once connected, you can send a natural language query as follows:

    ```javascript
    const query = 'What are the latest projects?';
    socket.send(query);
    ```

3. **Receive a Response:** The server will process your query and send back a response through the WebSocket. Handle this in the `onmessage` event.

### Example Workflow

- **Connecting:** A frontend application establishes a WebSocket connection using the `user_id` and a valid token.
- **Sending Queries:** The user types a question (e.g., "Show me employee performance scores") and sends it through the WebSocket.
- **Receiving Responses:** The application listens for messages and displays the response when it arrives.

