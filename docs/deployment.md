# Free Streamlit deployment

1. Make sure the updated project is pushed to [the GitHub repository](https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project).
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub. Complete account setup if this is your first visit.
3. Select **Create app**, then the option to deploy an app from GitHub.
4. Choose repository `Divyansh1-3/Emotion-Detection-from-Text-Project`, branch `main`, and main file `app.py`.
5. In **Advanced settings**, choose **Python 3.13**. Leave secrets empty.
6. Select **Deploy**. Wait for the first package installation to finish.
7. Open the resulting `streamlit.app` URL. Select the Joy example and click **Detect emotion**. Confirm that Joy and the score chart appear. Share that verified URL with your teacher.

The app uses Community Cloud's free hosting and no paid AI services. Initial deployment installs Python packages and takes longer than an ordinary visit. The laptop does not need to stay on once the cloud app is deployed. Free hosting has resource limits and may put an inactive app to sleep; an always-instant first visit is not guaranteed.

Do not upload the local `.venv`, backup folders, old ZIPs, `.env`, or old databases. The repository already includes the small model and all required application files.

If deployment fails, check the build logs. Confirm Python 3.13, `app.py`, and the pinned dependencies in `requirements.txt`. The app must include `model/emotion_model.pkl.gz`; it never downloads or trains a model during startup.

Official guides: [Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud) and [deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
