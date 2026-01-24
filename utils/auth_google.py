
import streamlit as st
from streamlit_oauth import OAuth2Component
import os
import json
import base64

class GoogleAuthManager:
    def __init__(self):
        # Allow user to provide credentials via secrets or environment variables
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID") or st.secrets.get("GOOGLE_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET") or st.secrets.get("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI") or st.secrets.get("GOOGLE_REDIRECT_URI", "http://localhost:8501")
        
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.revoke_url = "https://oauth2.googleapis.com/revoke"
        
    def login(self):
        """
        Handles the Google OAuth2 flow.
        Returns user email if successful, or None.
        """
        if not self.client_id or not self.client_secret:
            st.error("⚠️ Google Auth Config Missing")
            st.info("Please set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.streamlit/secrets.toml` or environment variables.")
            
            # Temporary setup input for user testing
            with st.expander("🔧 Developer Setup (One-time)"):
                c_id = st.text_input("Client ID")
                c_s = st.text_input("Client Secret", type="password")
                if c_id and c_s:
                    os.environ["GOOGLE_CLIENT_ID"] = c_id
                    os.environ["GOOGLE_CLIENT_SECRET"] = c_s
                    st.rerun()
            return None

        oauth2 = OAuth2Component(
            self.client_id, 
            self.client_secret, 
            self.auth_url, 
            self.token_url, 
            self.token_url, 
            self.revoke_url
        )
        
        # Check if code is in query params (redirect callback)
        if 'code' in st.query_params:
            result = oauth2.authorize_button(
                name="Continue with Google",
                icon="https://www.google.com/chrome/static/images/chrome-logo.svg",
                redirect_uri=self.redirect_uri,
                scope="openid email profile",
                key="google_auth_btn",
                use_container_width=True
            )
        else:
            result = oauth2.authorize_button(
                name="Continue with Google",
                icon="https://www.google.com/chrome/static/images/chrome-logo.svg",
                redirect_uri=self.redirect_uri,
                scope="openid email profile",
                key="google_auth_btn",
                use_container_width=True
            )
            
        if result and 'token' in result:
             # Decode ID Token to get email
            id_token = result.get('id_token')
            if id_token:
                # Basic decoding without validation (libs like google-auth do verify)
                # For this demo, we extract the payload
                payload = id_token.split('.')[1]
                # Pad base64
                payload += '=' * (-len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload).decode('utf-8'))
                email = decoded.get('email')
                return email
                
        return None
