from flask import Flask, render_template, request
from mbta_helper import find_stop_near

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    # Just show the greeting + form
    return render_template("index.html")


@app.route("/nearest_mbta", methods=["POST"])
def nearest_mbta():
    """
    Handle form submission:
    - Read place from form
    - Validate it
    - Call mbta_helper.find_stop_near
    - Render result or error
    """
    place = request.form.get("place", "").strip()

    if not place:
        error_message = "Please enter a valid place name."
        return render_template("error.html", error=error_message)

    try:
        stop_name, is_accessible, weather = find_stop_near(place)
        return render_template(
            "mbta_station.html",
            place=place,
            stop_name=stop_name,
            is_accessible=is_accessible,
            weather=weather,
        )
    except Exception as e:
        # Something went wrong with API / lookup
        return render_template("error.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True)

