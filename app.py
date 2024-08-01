from flask import Flask, render_template, request, jsonify, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import pickle
import requests

app = Flask(__name__, template_folder='template')
file = open("crop_rec.pkl" ,'rb')
model = pickle.load(file)

RAPIDAPI_KEY = "f83c41d76bmshae51ad0225a1149p11373fjsn32704c866272"
WEATHER_API_URL = "https://weatherapi-com.p.rapidapi.com/current.json"
API_KEY = "YOUR_API_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farming_equipment.db'
db = SQLAlchemy(app)
# Define the FarmEquipment model
class FarmEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.Integer,nullable=False)
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)

# index function
@app.route('/',methods=['GET'])
def index():
  weather_data = get_weather()
  return render_template('home.html', weather_data=weather_data)
   
def get_user_location():
    response = requests.get("https://ipinfo.io/json")
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_weather():
    user_location = get_user_location()
    if user_location and 'loc' in user_location:
        lat_lon = user_location['loc']
    else:
        # Default to a location of kathmandu
        lat_lon = "27.700769,-85.300140" 

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    querystring = {"q": lat_lon}

    response = requests.get(WEATHER_API_URL, headers=headers, params=querystring)

    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        return None


# rental function
@app.route("/rental",methods=['POST','GET'])
def show():
    # Create the database
    db.create_all()
    equipment_list = FarmEquipment.query.all()
    return render_template('rental.html', equipment_list=equipment_list)

@app.route('/rent/<int:id>')
def rent(id):
    equipment = FarmEquipment.query.get(id)
    if equipment:
        equipment.available = False
        db.session.commit()
    return redirect(url_for('rental'))

@app.route('/hire/<int:id>')
def hire(id):
    equipment = FarmEquipment.query.get(id)
    if equipment:
        equipment.available = True
        db.session.commit()
    return redirect(url_for('rental'))

# route to handle adding equipment
@app.route('/add_equipment', methods=['POST'])
def add_equipment():
    name = request.form['name']
    contact = request.form['contact']
    description = request.form['description']
    new_equipment = FarmEquipment(name=name, contact=contact,description=description)
    db.session.add(new_equipment)
    db.session.commit()
    
    return redirect(url_for('rental'))

# route to handle deleting equipment
@app.route('/delete_equipment/<int:id>')
def delete_equipment(id):
    equipment = FarmEquipment.query.get(id)
    if equipment:
        db.session.delete(equipment)
        db.session.commit()
    return redirect(url_for('rental'))




# @app.route("/crop", methods = ['POST', 'GET'])
# def crop():
#    return(render_template("crop.html"))

# crop function
@app.route("/crop", methods=['POST', 'GET'])
def crop_result():
   prediction_message = ""  # Initialize with a default value

   if request.method == 'POST':
      input_data = request.get_json()

      if not all(key in input_data for key in ("nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall")):
         return jsonify({"error": "Invalid JSON structure"}), 400

      input_list = [input_data[key] for key in ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]]

      prediction = model.predict([input_list])[0]
      crop_dict = {
                    0:"rice",
                    1:"maize",
                    2:"jute",
                    3:"cotton",
                    4:"coconut",
                    5:"papaya",
                    6:"orange",
                    7:"apple",
                    8:"muskmelon",
                    9:"watermelon",
                    10:"grapes",
                    11:"mango",
                    12:"banana",
                    13:"pomegranate",
                    14:"lentil",
                    15:"blackgram",
                    16:"mungbean",
                    17:"mothbeans",
                    18:"pigeonpeas",
                    19:"kidneybeans",
                    20:"chickpea",
                    21:"coffee"
        }
      if prediction in crop_dict:
        prediction_message = crop_dict[prediction]
      else:
         prediction_message = "TRY again"
      print(prediction_message)
      return jsonify({"prediction":prediction_message})
   return (render_template("crop.html"))

@app.route("/disease", methods = ['GET', 'POST'])
def disease():
   return render_template("disease.html")

@app.route("/portfolio", methods = ['GET', 'POST'])
def portfolio():
   return render_template("protofilo.html")

if __name__ == "__main__":
   app.run(debug=True)