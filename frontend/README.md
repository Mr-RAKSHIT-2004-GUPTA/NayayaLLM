# NayayaLLM — Legal Document Intelligence

This is a Next.js application that provides AI-powered analysis for legal documents using a FastAPI backend.

## Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing.

### Prerequisites

- [Node.js](https://nodejs.org/) (version 20 or later recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)
- Your own running instance of the FastAPI backend.

### Setup

1.  **Clone the repository or download the code:**
    If you haven't already, get the project code onto your local machine.

2.  **Install Dependencies:**
    Navigate to the root directory of the project in your terminal and run the following command to install all the necessary packages:
    ```bash
    npm install
    ```

3.  **Configure Backend URL:**
    This project needs to connect to your FastAPI backend.
    -   In the root of the project, you will find a file named `.env.local`.
    -   Open this file and update the `FASTAPI_BACKEND_URL` with the address of your running FastAPI server. For example:
        ```
        FASTAPI_BACKEND_URL=http://127.0.0.1:8000
        ```

### Running the Application

1.  **Start your FastAPI Backend:**
    Ensure your Python-based FastAPI server is running before you start the Next.js application.

2.  **Start the Development Server:**
    Once the setup is complete, run the following command in the project's root directory:
    ```bash
    npm run dev
    ```

3.  **Open the App:**
    The application will now be running. You can view it in your browser at:
    [http://localhost:9002](http://localhost:9002)

The app will automatically reload if you make any changes to the code.
