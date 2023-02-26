import io
from flask import Flask, jsonify, render_template ,request, send_from_directory , send_file
from folium import ClickForMarker, Map
import folium
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np 
import pandas as pd
import pickle
from joblib import load
import xlsxwriter
import json 

app = Flask(__name__, static_folder="templates/static")
result=0
regressor = pickle.load(open("GBR_with_depth_v3_withoutdate.pkl", "rb"))
markers = []

reg = load('GBR_MODEL_best2.joblib')
@app.route("/")
@app.route("/home")
def page():

    return render_template('home.html')
    
@app.route("/csvPredict")
def page1():
    return render_template('ExcelPrediction.html')

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        LONGITUDE  = request.form.get('LONGITUDE')
        LATITUDE   = request.form.get('LATITUDE')
        ALKALI     = request.form.get('ALKALI')
        TCARBN     = request.form.get('TCARBN')
        DEPTH     = request.form.get('DEPTH')
        # DATE       = request.form.get('DATE')
        # result     = randomForest.predict([[ -172.1040,	24.0695, 20051204.0	,34.1637,2285.7,2300.8]] ) 
        print("0000000000000000000000032222222222200000000000000000")
        # result    = reg.predict([[float(LONGITUDE),float(LATITUDE) , int(DATE) ,float(DEPTH),float(TCARBN), float(ALKALI)]] )
        result    = regressor.predict([[float(LONGITUDE),float(LATITUDE) ,float(DEPTH),float(TCARBN), float(ALKALI)]] )
    return jsonify(result=result[0])



# ........................................................................................

@app.route("/upload1212", methods=['GET', 'POST'])
def index():
    print("i ama in ")
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Read the uploaded file
            df = pd.read_excel(file)

            # TODO: Call your machine learning model to predict pH values
            # Here, we just add a new column with zeros to demonstrate how to create a new Excel file
            df['pH_predicted'] = regressor.predict(df)

            # Create a new Excel file with the predicted pH values
            excel_file = pd.ExcelWriter('predicted_ph.xlsx', engine='xlsxwriter')
            df.to_excel(excel_file, sheet_name='Sheet1', index=False)
            excel_file.save()

            return send_file('predicted_ph.xlsx', as_attachment=True)

    return '''
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    '''
# ========================================================================


import traceback

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_excel(file)
    markers = []

    for index, row in df.iterrows():
        lat = row['LATITUDE']
        print("lattttttttttttttttttttt======= : ",lat);
        lon = row['LONGITUDE']
        depth = row['DEPTH']
        alkali = row['ALKALI']
        tcarbn = row['TCARBN']
        pH_value = regressor.predict([[lat, lon,depth ,alkali,tcarbn]])
        print('we r here 1',index)

        markers.append({'lat': lat, 'lon': lon, 'depth':depth, 'pH_value':  float(pH_value)})
        
        print('we r here 2',index)
    # Render the map template with the markers
    markers_json = json.dumps(markers)
    return render_template('draw.html', markers=markers_json)


    # # Call your machine learning model to predict pH values based on the input Excel file
    # df['pH_predicted'] = reg.predict(df)
    # # Generate a new Excel file with the predicted pH values
    # output_df =df
    # output_file = io.BytesIO()
    # writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    # output_df.to_excel(writer, sheet_name='Sheet1', index=False)
    # writer.save()
    # output_file.seek(0)
 
    # return send_file(output_file, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True,download_name="predicted_ph.csv")



if __name__ == '__main__':
    app.run(debug= True , port=5002)



    
