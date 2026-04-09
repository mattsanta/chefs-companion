# Chef's Companion

## Project Description

Chef's Companion is a web application designed to help users manage and discover recipes. It provides functionalities for viewing recipes, and potentially managing user-generated content like recipe ratings and uploads.

## Setup Instructions

To set up the project locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/chefs-companion.git
    cd chefs-companion
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## How to Run

To run the application, ensure your virtual environment is activated and then execute:

```bash
python app.py
```

The application should then be accessible in your web browser at `http://127.0.0.1:5000` (or similar, as indicated by the Flask server).

## Contribution

See `CONTRIBUTING.md` for guidelines on how to contribute to this project.

hello from yesh and matt
## CI/CD Pipeline

This project uses Google Cloud Build and Cloud Deploy to automatically deploy to GKE.

### Environments
- **Dev**: Automatically deployed on every push to the `main` branch.
- **Prod**: Automatically promoted after a successful deployment to Dev.

### Features
- **Automatic Rollbacks**: If a deployment fails in any environment, it will be automatically rolled back to the previous stable version.
- **Infrastructure as Code**: Managed via Terraform in the `terraform/` directory.

### Manual Actions
- You can monitor deployments in the [Google Cloud Console](https://console.cloud.google.com/deploy/delivery-pipelines).
- Releases can also be manually created using `gcloud deploy releases create`.
