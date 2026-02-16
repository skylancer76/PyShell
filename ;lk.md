# Deployment Guide

This guide explains how to completely remove the existing deployment and redeploy the PyShell application correctly on Vercel.

## 1. Clean Up Existing Deployments

Before starting, it's best to remove the potentially conflicting or broken deployments to start fresh.

1.  Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2.  Find the existing project(s) for PyShell (you might have one or two depending on how you deployed).
3.  Go to **Settings** -> **General**.
4.  Scroll to the bottom and click **Delete Project**.
5.  Confirm the deletion.

---

## 2. Deploy the Backend (Python)

We need to deploy the backend first to get the API URL.

1.  Open your terminal in the project root.
2.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
3.  Deploy using the Vercel CLI:
    ```bash
    vercel
    ```
    - **Set up and deploy?** [Y]
    - **Which scope?** [Select your account]
    - **Link to existing project?** [N]
    - **What's your project's name?** `pyshell-backend` (or similar)
    - **In which directory is your code located?** `./` (Press Enter)
    - **Want to modify these settings?** [N] (The `vercel.json` file handles the config)

4.  Wait for the deployment to complete.
5.  **Copy the Production URL** from the output (e.g., `https://pyshell-backend.vercel.app`).
    - *Note: You can verify it works by visiting `https://pyshell-backend.vercel.app/health` in your browser. It should say `{"status": "ok"}`.*

---

## 3. Deploy the Frontend (React)

Now we deploy the frontend and tell it where the backend lives.

1.  Open a new terminal or go back to the root, then navigate to the frontend folder:
    ```bash
    cd ../frontend
    ```
    *(Ensure you are in `PyShell/frontend`)*

2.  Deploy using the Vercel CLI:
    ```bash
    vercel
    ```
    - **Set up and deploy?** [Y]
    - **Which scope?** [Select your account]
    - **Link to existing project?** [N]
    - **What's your project's name?** `pyshell-frontend`
    - **In which directory is your code located?** `./` (Press Enter)
    - **Want to modify these settings?** [Y] **(IMPORTANT)**

3.  **Build Command**: `vite build` (Default is usually correct, but verify)
4.  **Output Directory**: `dist` (Default is usually correct)
5.  **Install Command**: `npm install` (Default is usually correct)

6.  **Environment Variables**:
    - When asked "Want to modify these settings?", select **Environment Variables** if offered in the CLI, OR...
    - **Easier Method**: Let it deploy once (it might fail to connect), then go to the Vercel Dashboard for `pyshell-frontend`.
    - Go to **Settings** -> **Environment Variables**.
    - Add a new variable:
        - **Key**: `VITE_API_URL`
        - **Value**: `https://pyshell-backend.vercel.app` (The Backend URL you copied earlier, **without** the trailing slash `/`)
    - Click **Save**.

7.  **Redeploy** (if you added env vars in the dashboard):
    - Go to **Deployments** tab.
    - Click the three dots on the latest deployment -> **Redeploy**.
    - Ensure the "Use existing Build Cache" is **unchecked** if you want to be safe, or just redeploy.

---

## 4. Verification

1.  Open your Frontend URL (e.g., `https://pyshell-frontend.vercel.app`).
2.  The terminal should load.
3.  You should see a message saying "Backend connected".
4.  Try typing `help` or `ls`. If it responds, everything is working!
