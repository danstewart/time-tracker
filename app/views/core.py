from flask import Blueprint, render_template

v = Blueprint("core", __name__)


# @v.get("/frames/<frame>")
# def render_frame(frame: str):
#     """
#     Default handler for rendering frames
#     """
#     return render_template("frames/{}.html.j2".format(frame))
