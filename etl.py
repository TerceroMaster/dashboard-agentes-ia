import pandas as pd
import sqlite3
import os
import unicodedata
import random
import numpy as np

# Paths
EXCEL_PATH = r"c:\Proyectos IA Antigravity\4.- sitios-webs\maestro-valencia\dashboard-power-bi\info-ejemplo1\Estadísticas PIRMCT 2025.xlsx"
SINOPEC_PATH = r"c:\Proyectos IA Antigravity\4.- sitios-webs\maestro-valencia\dashboard-power-bi\info-ejemplo2\372-Lista de Puntos de Acción-160222 - copia.xlsx"
RETAIL_PATH = r"c:\Proyectos IA Antigravity\4.- sitios-webs\maestro-valencia\dashboard-power-bi\info-ejemplo3\superstore.csv"
TWITTER_PATH = r"c:\Proyectos IA Antigravity\4.- sitios-webs\maestro-valencia\dashboard-power-bi\info-ejemplo4\training.1600000.processed.noemoticon.csv"
AIRLINES_PATH = r"c:\Proyectos IA Antigravity\4.- sitios-webs\maestro-valencia\dashboard-power-bi\info-ejemplo5\airlines.csv"
DB_PATH = "dashboard_data.db"

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', str(input_str))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_cols(df):
    df.columns = [remove_accents(str(c)).strip().replace(' ', '_').lower() for c in df.columns]
    return df

def main():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. PIRMCT
    try:
        print("Loading PIRMCT...")
        df_pirmct = pd.read_excel(EXCEL_PATH, sheet_name="Total")
        df_pirmct = clean_cols(df_pirmct)
        df_pirmct.to_sql("pirmct_total", conn, if_exists="replace", index=False)
        print(f"PIRMCT loaded: {len(df_pirmct)} rows")
    except Exception as e:
        print(f"Error PIRMCT: {e}")

    # 2. SINOPEC
    try:
        print("Loading Sinopec...")
        df_sinopec = pd.read_excel(SINOPEC_PATH, header=2)
        df_sinopec = clean_cols(df_sinopec)
        df_sinopec.to_sql("sinopec_total", conn, if_exists="replace", index=False)
        print(f"Sinopec loaded: {len(df_sinopec)} rows")
    except Exception as e:
        print(f"Error Sinopec: {e}")

    # 3. RETAIL (SUPERSTORE)
    try:
        print("Loading Retail (Superstore)...")
        # Handle the encoding and drop the weird Chinese column by index if needed, or just let it pass and rename
        df_retail = pd.read_csv(RETAIL_PATH, encoding='latin1')
        df_retail = clean_cols(df_retail)
        # Drop column if it looks like garbage
        cols_to_drop = [c for c in df_retail.columns if '?' in c or '\x95' in c or '记' in c or len(c.strip()) == 0]
        if cols_to_drop:
            df_retail.drop(columns=cols_to_drop, inplace=True)
        df_retail.to_sql("retail_total", conn, if_exists="replace", index=False)
        print(f"Retail loaded: {len(df_retail)} rows")
    except Exception as e:
        print(f"Error Retail: {e}")

    # 4. TWITTER SENTIMENT
    try:
        print("Loading Twitter Sentiment (Sampling 10k rows)...")
        # Load exactly 10,000 rows randomly to avoid breaking Streamlit/SQLite size limits
        # Using skiprows logic to sample efficiently
        n = sum(1 for _ in open(TWITTER_PATH, encoding='latin1')) - 1
        s = 10000 
        skip = sorted(random.sample(range(1, n+1), n-s)) 
        
        df_tw = pd.read_csv(TWITTER_PATH, encoding='latin1', header=None, skiprows=skip)
        df_tw.columns = ['target', 'id', 'date', 'flag', 'user', 'text']
        
        # Map target: 0=Negative, 4=Positive
        df_tw['sentiment'] = df_tw['target'].map({0: 'Negativo', 2: 'Neutral', 4: 'Positivo'})
        df_tw.to_sql("twitter_total", conn, if_exists="replace", index=False)
        print(f"Twitter loaded: {len(df_tw)} rows")
    except Exception as e:
        print(f"Error Twitter: {e}")

    # 5. AIRLINES / LOGISTICS
    try:
        print("Loading Airlines and Generating Synthetic Flights...")
        df_airlines = pd.read_csv(AIRLINES_PATH)
        df_airlines = clean_cols(df_airlines)
        
        # Generate synthetic flights connecting major global cities
        cities = [
            {"name": "Nueva York", "lat": 40.7128, "lon": -74.0060},
            {"name": "Londres", "lat": 51.5074, "lon": -0.1278},
            {"name": "Tokio", "lat": 35.6762, "lon": 139.6503},
            {"name": "París", "lat": 48.8566, "lon": 2.3522},
            {"name": "Dubai", "lat": 25.2048, "lon": 55.2708},
            {"name": "Sídney", "lat": -33.8688, "lon": 151.2093},
            {"name": "Ciudad de México", "lat": 19.4326, "lon": -99.1332},
            {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333},
            {"name": "Singapur", "lat": 1.3521, "lon": 103.8198},
            {"name": "Frankfurt", "lat": 50.1109, "lon": 8.6821}
        ]
        
        flights = []
        # Create 500 random flights
        airline_codes = df_airlines['iata_code'].dropna().tolist()
        
        for _ in range(500):
            origin = random.choice(cities)
            dest = random.choice(cities)
            while dest['name'] == origin['name']:
                dest = random.choice(cities)
                
            airline = random.choice(airline_codes) if airline_codes else "UNK"
            status = np.random.choice(["A Tiempo", "Demorado", "Cancelado"], p=[0.8, 0.15, 0.05])
            
            flights.append({
                "airline": airline,
                "origin_city": origin["name"],
                "origin_lat": origin["lat"],
                "origin_lon": origin["lon"],
                "dest_city": dest["name"],
                "dest_lat": dest["lat"],
                "dest_lon": dest["lon"],
                "status": status,
                "passengers": random.randint(50, 350)
            })
            
        df_flights = pd.DataFrame(flights)
        df_flights = df_flights.merge(df_airlines, left_on='airline', right_on='iata_code', how='left')
        df_flights['airline_name'] = df_flights['airline_y'].fillna("Aerolínea Desconocida")
        
        df_flights.to_sql("flights_total", conn, if_exists="replace", index=False)
        print(f"Logistics (Flights) loaded: {len(df_flights)} rows")
    except Exception as e:
        print(f"Error Logistics: {e}")

    conn.close()
    print("ETL complete!")

if __name__ == "__main__":
    main()
