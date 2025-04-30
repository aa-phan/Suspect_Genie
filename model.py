import pandas as pd
import numpy as np
from tensorflow import keras
from joblib import load
model = keras.models.load_model('neural_net_model.h5', compile=False)
label_encoders = load('label_encoders.bin')
scaler = load('standard_scaler.bin')

categorical_cols = list(label_encoders.keys())
numerical_cols = [
    'Length', 'Width', 'Height', 'Weight',
    'Volume',
    'weight_to_volume',
    'length_to_width', 'length_to_height', 'width_to_height',
    'length_squared', 'width_squared', 'height_squared',
    'dimension_std',
    'base_area_to_height',
    'log_weight',
    'cubed_length', 'cubed_width', 'cubed_height',
    'cube_root_volume', 'square_root_volume',
    'weight*volume',
    'weight*length',
    'length/(width+height)', 'width/(length+height)', 'height/(length+width)',
    'weight/volume',
    'weight**2/volume',
    'Surface_Area',
    'Diagonal',
    'max_dimension', 'min_dimension', 'dimension_range',
    'total_dimension',
    'length_fraction', 'width_fraction', 'height_fraction',
    'weight_times_total_dimension',
    'diff_length_width', 'diff_length_height', 'diff_width_height',
    'SA_to_Volume',
        'log_Surface_Area',
        'log_SA_to_Volume'
    ]

def predict_package_suspects(csv_path, threshold, batch_size=512):
    # Load model

    # Read and preprocess CSV
    print("Reading CSV...")
    df = pd.read_csv(csv_path)

    # Feature engineering
    #Volume
    df['Volume'] = df['Length']*df['Width']*df['Height']
    #Weight/Volume Ratio
    df['weight_to_volume'] = df['Weight']/df['Volume']
    #Dimension Ratios
    df['length_to_width'] = df['Length']/df['Width']
    df['length_to_height'] = df['Length']/df['Height']
    df['width_to_height'] = df['Width']/df['Height']

    df['length_squared'] = df['Length']**2
    df['width_squared'] = df['Width']**2
    df['height_squared'] = df['Height']**2


    df['dimension_std'] = df[['Length', 'Width', 'Height']].std(axis=1)

    df['base_area_to_height'] = (df['Length']*df['Width'])/df['Height']

    df['log_weight'] = np.log(df['Weight']+1)

    df['cubed_length'] = df['Length']**3
    df['cubed_width'] = df['Width']**3
    df['cubed_height'] = df['Height']**3

    df['cube_root_volume'] = df['Volume']**(1/3)

    df['square_root_volume'] = df['Volume']**(1/2)

    df['weight*volume'] = df['Weight']*df['Volume']

    df['weight*length'] = df['Weight']*df['Length']

    df['length/(width+height)'] = df['Length'] / (df['Width'] + df['Height'])
    df['width/(length+height)'] = df['Width'] / (df['Length'] + df['Height'])
    df['height/(length+width)'] = df['Height'] / (df['Length'] + df['Width'])

    df['weight/volume'] = df['Weight']/df['Volume']

    df['weight**2/volume'] = (df['Weight']**2)/df['Volume']

    # Surface Area
    df['Surface_Area'] = 2 * (
        df['Length'] * df['Width'] +
        df['Length'] * df['Height'] +
        df['Width'] * df['Height']
    )

    # Diagonal Length
    df['Diagonal'] = np.sqrt(
        df['Length']**2 + df['Width']**2 + df['Height']**2
    )

    # Dimension Comparison Features

    # Max, Min, and Range of Dimensions
    df['max_dimension'] = df[['Length', 'Width', 'Height']].max(axis=1)
    df['min_dimension'] = df[['Length', 'Width', 'Height']].min(axis=1)
    df['dimension_range'] = df['max_dimension'] - df['min_dimension']

    # Fractions of Dimensions
    df['total_dimension'] = df['Length'] + df['Width'] + df['Height']
    df['length_fraction'] = df['Length'] / df['total_dimension']
    df['width_fraction'] = df['Width'] / df['total_dimension']
    df['height_fraction'] = df['Height'] / df['total_dimension']
    # Composite & Interaction Features
    df['weight_times_total_dimension'] = df['Weight'] * df['total_dimension']

    # Differences Between Dimensions
    df['diff_length_width'] = abs(df['Length'] - df['Width'])
    df['diff_length_height'] = abs(df['Length'] - df['Height'])
    df['diff_width_height'] = abs(df['Width'] - df['Height'])
    # Efficiency Metrics
    df['SA_to_Volume'] = df['Surface_Area'] / (df['Volume'] + 1e-8)  # add epsilon to avoid division by 0

    # Log transformations of composite features
    df['log_Surface_Area'] = np.log(df['Surface_Area']+1)

    df['log_SA_to_Volume'] = np.log(df['SA_to_Volume']+1)
    """
    # Ensure feature alignment
    cat_inputs = []
    for col in categorical_cols:
        encoded = label_encoders[col].transform(df[col].astype(str)).reshape(-1,1)
        cat_inputs.append(encoded)
    
    numerical_data = scaler.transform(df[numerical_cols].values)
    cat_inputs.append(numerical_data)
    """
    model_inputs = {}
    for col in categorical_cols:
        model_inputs[col] = label_encoders[col].transform(df[col].astype(str)).reshape(-1,1)
    
    
    model_inputs["numerical_input"] = scaler.transform(df[numerical_cols].values)
    
    # Predict
    print("Generating predictions...")
    preds = model.predict(model_inputs, batch_size=batch_size).flatten()
    predicted_labels = (preds > threshold).astype(int)
    
    # Format output
    df['Suspect'] = predicted_labels
    df['Probability'] = preds

    return df[['SKU', 'DESCRIPTION','Suspect', 'Probability']]
