import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import glob
import os

def load_trading_data(base_path):
    """
    Load market and trade data from multiple directories
    
    Args:
        base_path (str): Base directory containing trading data
    
    Returns:
        pd.DataFrame: Merged and preprocessed trading data
    """
    all_market_data = []
    all_trade_data = []
    
    # Updated glob pattern to match your specific directory structure
    for period in range(1, 10):  # Periods 1-9
        for location in ['A', 'B', 'C', 'D', 'E']:
            market_pattern = os.path.join(base_path, f'Period{period}', location, f'market_data_{location}.csv')
            trade_pattern = os.path.join(base_path, f'Period{period}', location, f'trade_data_{location}.csv')
            
            # Load market data
            market_files = glob.glob(market_pattern)
            for market_file in market_files:
                try:
                    market_df = pd.read_csv(market_file)
                    market_df['source'] = 'market'
                    market_df['period'] = period
                    market_df['location'] = location
                    all_market_data.append(market_df)
                except Exception as e:
                    print(f"Error loading market file {market_file}: {e}")
            
            # Load trade data
            trade_files = glob.glob(trade_pattern)
            for trade_file in trade_files:
                try:
                    trade_df = pd.read_csv(trade_file)
                    trade_df['source'] = 'trade'
                    trade_df['period'] = period
                    trade_df['location'] = location
                    all_trade_data.append(trade_df)
                except Exception as e:
                    print(f"Error loading trade file {trade_file}: {e}")
    
    # Combine data
    market_data = pd.concat(all_market_data, ignore_index=True) if all_market_data else pd.DataFrame()
    trade_data = pd.concat(all_trade_data, ignore_index=True) if all_trade_data else pd.DataFrame()
    
    print(f"Loaded {len(market_data)} market data rows and {len(trade_data)} trade data rows")
    
    return market_data, trade_data

def preprocess_data(market_data, trade_data):
    """
    Preprocess and merge market and trade data
    
    Args:
        market_data (pd.DataFrame): Market order book data
        trade_data (pd.DataFrame): Trade execution data
    
    Returns:
        pd.DataFrame: Merged and feature-engineered dataset
    """
    # Convert timestamp to datetime
    market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
    trade_data['timestamp'] = pd.to_datetime(trade_data['timestamp'])
    
    # Merge data based on timestamp
    merged_data = pd.merge_asof(
        market_data.sort_values('timestamp'), 
        trade_data.sort_values('timestamp'),
        on='timestamp', 
        direction='nearest'
    )
    
    # Feature engineering
    merged_data['bid_ask_spread'] = merged_data['askPrice'] - merged_data['bidPrice']
    merged_data['volume_imbalance'] = merged_data['bidVolume'] - merged_data['askVolume']
    
    # Create target variable (next microsecond price)
    merged_data['next_price'] = merged_data['price'].shift(-1)
    
    # Drop rows with NaN
    merged_data.dropna(inplace=True)
    
    return merged_data

def train_price_prediction_model(merged_data):
    """
    Train a machine learning model to predict next microsecond price
    
    Args:
        merged_data (pd.DataFrame): Preprocessed trading data
    
    Returns:
        dict: Model, scaler, and performance metrics
    """
    # Select features and target
    features = [
        'bidVolume', 'bidPrice', 'askVolume', 'askPrice', 
        'price', 'volume', 'bid_ask_spread', 'volume_imbalance'
    ]
    X = merged_data[features]
    y = merged_data['next_price']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    return {
        'model': model,
        'scaler': scaler,
        'mse': mse,
        'rmse': rmse
    }

def main(base_path):
    """
    Main function to load, preprocess, and train model
    
    Args:
        base_path (str): Base directory for trading data
    """
    # Load data
    market_data, trade_data = load_trading_data(base_path)
    
    # Preprocess data
    merged_data = preprocess_data(market_data, trade_data)
    
    # Train model
    results = train_price_prediction_model(merged_data)
    
    print(f"Model Performance:")
    print(f"Mean Squared Error: {results['mse']}")
    print(f"Root Mean Squared Error: {results['rmse']}")

# Example usage
if __name__ == '__main__':
    base_path = './TradingData'
    main(base_path)