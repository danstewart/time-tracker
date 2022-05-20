from flask import Blueprint, render_template

v = Blueprint("core", __name__)

@v.get("/about")
def about_page():
    return render_template("pages/about.html.j2")

