import pickle
import pandas as pd
from flask import Flask, request, jsonify

with open("./model/artifacts/model.pkl", "rb") as file_import:
    (dv, model) = pickle.load(file_import)


app = Flask('house-price-prediction')

def data_prep (house_features):
    property_type_map = {
        'house'                 : 1,
        'duplex-semi-detached'  : 2,
        'villa'                 : 3,
        'townhouse'             : 4,
        'terrace'               : 5,
        'apartment'             : 6,
        'flat'                  : 6,  # Same as apartment
        'unit'                  : 6,  # Same as apartment
        'acreage'               : 7,  # Based on land median
        'residential-other'     : 8
    }
    house_features["Property_Type"] = property_type_map.get(house_features["Property_Type"], 0)

    return house_features


def prediction(model, house_features):
    df = pd.DataFrame([house_features])
    
    X = dv.transform(df)
    pred_ = model.predict(X)
    y_pred = float(pred_[0])
    return y_pred


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    house = request.get_json()

    house_features = data_prep(house)
    pred = prediction(model, house_features)

    result = {
        "Potential price for this property": pred
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)