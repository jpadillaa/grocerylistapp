from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def list_view():
    return render_template("list.html")

@views_bp.route("/add")
def add_view():
    return render_template("add.html")

@views_bp.route("/categories")
def categories_view():
    return render_template("categories.html")

@views_bp.route("/stats")
def stats_view():
    return render_template("stats.html")
