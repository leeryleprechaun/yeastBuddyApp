from flask import Flask, request
from flask import jsonify
from flask import render_template
import pymongo
from pymongo import MongoClient
import json
from bson import json_util

cluster = MongoClient(
    "mongodb+srv://matthew:12345@cluster0.mmnlg8w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

db = cluster["MSDS_696"]
collection_yeast = db["yeast"]
collection_style = db["style"]


app = Flask(__name__)

supplier_list = [
    {"name": "Brewing Science Institute"},
    {"name": "Inland Island"},
    {"name": "Imperial"},
    {"name": "Omega"},
    {"name": "Propagate Lab"},
    {"name": "White Labs"},
    {"name": "Wyeast"},
]


@app.route("/")
def hello():
    return render_template("home.html")


@app.route("/supplier")
def supplier():
    # Fetching supplier data from MongoDB
    supplier_list = collection_yeast.distinct("Supplier")

    # Pass supplier data to the template for rendering
    return render_template("supplier2.html", suppliers=supplier_list)


@app.route("/supplier/<supplier_name>")
def supplier_offerings(supplier_name):
    # Fetch offerings for the selected supplier from MongoDB
    offerings = collection_yeast.find({"supplier": supplier_name})

    # Pass offerings data to the template for rendering
    return render_template(
        "offerings.html", supplier=supplier_name, offerings=offerings
    )


@app.route("/supplier/Brewing Science Institute", methods=["GET"])
def bsi():
    bsi = collection_yeast.find({"Supplier": "Brewing Science Institute"})
    bsi_list = list(bsi)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=bsi_list)


@app.route("/supplier/Imperial", methods=["GET"])
def find_imperial():
    imperial = collection_yeast.find({"Supplier": "Imperial"})
    imperial_list = list(imperial)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=imperial_list)


@app.route("/supplier/Inland Island", methods=["GET"])
def find_inland_island():
    inland_island = collection_yeast.find({"Supplier": "Inland Island"})
    inland_island_list = list(inland_island)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=inland_island_list)


@app.route("/supplier/Omega", methods=["GET"])
def find_omega():
    omega = collection_yeast.find({"Supplier": "Omega"})
    omega_list = list(omega)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=omega_list)


@app.route("/supplier/Propagate Lab", methods=["GET"])
def find_propagate_lab():
    propagate_lab = collection_yeast.find({"Supplier": "Propagate Lab"})
    propagate_lab_list = list(propagate_lab)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=propagate_lab_list)


@app.route("/supplier/Wyeast", methods=["GET"])
def find_wyeast():
    wyeast = collection_yeast.find({"Supplier": "Wyeast"})
    wyeast_list = list(wyeast)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=wyeast_list)


@app.route("/supplier/White Labs", methods=["GET"])
def find_white_labs():
    white_labs = collection_yeast.find({"Supplier": "White Labs"})
    white_labs_list = list(white_labs)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=white_labs_list)


@app.route("/stylefilter", methods=["GET", "POST"])
def stylefilter():
    if request.method == "POST":
        style = request.form.get("style")
        if style is None:
            return jsonify({"error": "Style parameter is required"}), 400

        # Query the second collection to get the strains for the selected style
        strains_pipeline = [
            {"$match": {"Style": style}},
            {
                "$lookup": {
                    "from": "yeast",
                    "localField": "Strain",
                    "foreignField": "Strain",
                    "as": "strains",
                }
            },
            {
                "$unwind": "$strains"  # Unwind the 'strains' array to get separate documents
            },
            {
                "$project": {
                    "_id": 0,
                    "Strain": "$strains.Strain",
                    "Supplier": "$strains.Supplier",
                    "Description": "$strains.Description",
                }
            },
        ]
        strains_result = list(db["style"].aggregate(strains_pipeline))

        # Render the template with the selected style and strains
        return render_template(
            "stylefilter_result.html", style=style, strains=strains_result
        )

    # If request method is GET, render the template with the dropdown menu
    styles = get_all_styles()
    return render_template("stylefilter.html", styles=styles)


def get_all_styles():
    # Query the first collection to get a list of all unique styles
    styles = db["style"].distinct("Style")
    return styles


@app.route("/strain/<strain_name>")
def strain_info(strain_name):
    # Retrieve strain information from MongoDB based on the strain name
    strain = collection_yeast.find_one({"Strain": strain_name})
    if strain:
        return render_template("strain_info.html", strain=strain)
    else:
        return "Strain not found", 404


@app.route("/globallist", methods=["GET"])
def get_yeast():
    all_yeast = list(collection_yeast.find({}))
    return render_template("globallist.html", style="All Strains", strains=all_yeast)
    # return jsonify(all_yeast)


@app.route("/strainfilter")
def strain_filter():
    # Fetch all documents from collection_yeast
    documents = collection_yeast.find({}, {"_id": 0, "Strain": 1})

    # Extract Strain from documents
    strains = [doc["Strain"] for doc in documents]

    return render_template("strain_dropdown.html", strains=strains)


@app.route("/search_styles", methods=["POST"])
def search_styles():
    selected_strain = request.form.get("strain")

    # Perform a lookup in the collection_style collection based on the selected strain
    styles_for_strain = collection_style.find(
        {"Strain": selected_strain}, {"_id": 0, "Style": 1}
    )

    # Extract styles from the documents
    styles = [doc["Style"] for doc in styles_for_strain]

    return render_template(
        "styles_table.html", selected_strain=selected_strain, styles=styles
    )


if __name__ == "__main__":
    app.run(debug=True)
