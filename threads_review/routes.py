import os
import requests
from flask import redirect, request, render_template, session
from . import threads_review_bp

CLIENT_ID = os.getenv("THREADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("THREADS_CLIENT_SECRET")
REDIRECT_URI = os.getenv("THREADS_REDIRECT_URI")

AUTH_URL = "https://www.threads.net/oauth/authorize"
TOKEN_URL = "https://graph.threads.net/oauth/access_token"
API_BASE = "https://graph.threads.net/v1.0"


@threads_review_bp.route("/threads-review")
def review_page():
    return render_template("threads_review.html", results=None)


@threads_review_bp.route("/threads/login")
def threads_login():
    url = (
        f"{AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=threads_basic,threads_keyword_search"
    )
    return redirect(url)


@threads_review_bp.route("/threads/callback")
def threads_callback():
    code = request.args.get("code")
    token = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        },
    ).json()

    session["threads_token"] = token.get("access_token")
    return redirect("/threads-review")


@threads_review_bp.route("/threads/search", methods=["POST"])
def keyword_search():
    keyword = request.form.get("keyword")
    token = session.get("threads_token")

    resp = requests.get(
        f"{API_BASE}/keyword_search",
        params={
            "q": keyword,
            "search_type": "TOP",
            "fields": "id,text,username,permalink,timestamp",
            "access_token": token,
        },
    )

    data = resp.json().get("data", [])
    return render_template("threads_review.html", results=data)
