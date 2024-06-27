# Pyson Email Sender Application

This project is a simple Python-based email sender that utilizes SMTP to send emails. It is designed to run in a Docker container, making it easy to set up and use across different environments.

## Prerequisites

Before you can run this application, you will need:

### 1. Docker and Docker Compose

This application is containerized, which means you will need Docker and Docker Compose to run it. Here's how to install Docker Compose on your system:

#### Installing Docker Desktop

Docker Desktop includes Docker Compose and provides a simple way to manage Docker containers.

- **Windows and Mac:**
  - Download Docker Desktop from [Docker Hub](https://www.docker.com/products/docker-desktop).
  - Follow the installation instructions for your operating system.

- **Linux:**
  - Install Docker using your distribution's package manager. For example, on Ubuntu, you would use:
    ```bash
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io
    ```
  - Install Docker Compose:
    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

### 2. Environment Configuration

You need to set up an `.env` file in the root directory of this project with the necessary SMTP configuration. The required environment variables are:

- `SMTP_HOST`: The hostname of the SMTP server.
- `SMTP_PORT`: The port number of the SMTP server.
- `SENDER`: The email address of the sender.
- `PASSWORD`: The password for the sender's email account (used for SMTP authentication).

#### Example `.env` File

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SENDER=your-email@example.com
PASSWORD=yourpassword
```

### 3. Recipients List

This application requires a file named `./python/recipients.txt` in the project root, listing the email addresses to which emails will be sent, one per line.

#### Example `./python/recipients.txt` File

```recipients
user1@example.com
user2@example.com
user3@example.com
```

## Running the Application

Once Docker and Docker Compose are installed and you've configured your `.env` file and `recipients.txt`, 
you can start the application by running the following command in the terminal from the project directory:

```start
docker-compose up --build -d
```

This command builds the Docker image if it has not been built before, 
or if there are changes in the Dockerfile or the dependencies, 
and then starts the container in detached mode.

## Stopping the Application

To stop the running container, you can use:

```stop
docker-compose down
```

