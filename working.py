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
    return render_template("hello.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/supplier")
def supplier():
    return render_template("supplier.html", suppliers=supplier_list)


@app.route("/styles", methods=['GET'])
def get_styles():
    styles = get_available_styles()
    return jsonify({'styles': styles})


@app.route("/yeast", methods=["GET"])
def get_yeast():
    all_yeast = list(collection_yeast.find({}))
    return json.dumps(all_yeast, default=json_util.default)
    # return jsonify(all_yeast)


@app.route("/supplier/Omega", methods=["GET"])
def find_omega():
    omega = collection_yeast.find({"Supplier": "Omega"})
    omega_list = list(omega)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=omega_list)


@app.route("/filtered_results", methods=["GET"])
def filtered_results():
    try:
        # Extract filter parameters from request
        # filter_param = request.args.get("Omega")

        # Perform database query to filter results
        filtered_data = collection_yeast.find({"Supplier": "Omega"})

        # Convert MongoDB cursor to list of dictionaries
        filtered_data = list(filtered_data)

        if len(filtered_data) == 0:
            return jsonify({"message": "No results found for the given filter."}), 404

        # Return filtered results as JSON response
        return jsonify(json_util.dumps(filtered_data)), 200
        # return json.dumps(filtered_data, default=json_util.default)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # return json.dumps(omega_list, default=json_util.default)


@app.route("/filter", methods=["GET", "POST"])
def filter_supplier():
    try:
        if request.method == "POST":
            # Extract supplier name from the form submitted by the user
            supplier_name = request.form.get("supplier_name")

            # Perform database query to filter results
            if supplier_name:
                supplier = collection_yeast.find({"Supplier": supplier_name})
            else:
                supplier = collection_yeast.find(
                    {}
                )  # Return all documents if no filter is provided

            # Convert MongoDB cursor to list of dictionaries using json_util
            supplier_list = list(supplier)

            # Return the list as a JSON response
            # WORKING CODE return jsonify(json_util.dumps(supplier_list)), 200
            return render_template("results.html", supplier_list=supplier_list)
        else:
            # Render the HTML template containing the form
            return render_template("index.html")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/supplier/Brewing Science Institute", methods=["GET"])
def bsi():
    bsi = collection_yeast.find({"Supplier": "Brewing Science Institute"})
    bsi_list = list(bsi)
    # return json.dumps(omega_list, default=json_util.default)
    # return jsonify(omega_list)
    return render_template("results.html", supplier_list=bsi_list)



@app.route("/stylefilter", methods=['GET', 'POST'])
def stylefilter():
    if request.method == 'POST':
        style = request.form.get('style')
        if style is None:
            return jsonify({'error': 'Style parameter is required'}), 400

        # Query the second collection to get the strains for the selected style
        strains_pipeline = [
 {
                '$match': {
                    'Style': style
                }
            },
            {
                '$lookup': {
                    'from': 'yeast',
                    'localField': 'Strain',
                    'foreignField': 'Strain',
                    'as': 'strains'
                }
            },
            {
                '$unwind': '$strains'  # Unwind the 'strains' array to get separate documents
            },
            {
                '$project': {
                    '_id': 0,
                    'Strain': '$strains.Strain',
                    'Supplier': '$strains.Supplier',
                    'Description': '$strains.Description'
                }
            }
        ]
        strains_result = list(db['style'].aggregate(strains_pipeline))

        # Render the template with the selected style and strains
        return render_template('stylefilter_result.html', style=style, strains=strains_result)


    # If request method is GET, render the template with the dropdown menu
    styles = get_all_styles()
    return render_template('stylefilter.html', styles=styles)

def get_all_styles():
    # Query the first collection to get a list of all unique styles
    styles = db['style'].distinct('Style')
    return styles

@app.route('/strain/<strain_name>')
def strain_info(strain_name):
    # Retrieve strain information from MongoDB based on the strain name
    strain = collection_yeast.find_one({'Strain': strain_name})
    if strain:
        return render_template('strain_info.html', strain=strain)
    else:
        return 'Strain not found', 404

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)












