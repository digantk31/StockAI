"""
Real-time Data Streaming Module
Handles WebSocket connections for live stock price updates
"""
import asyncio
import websockets
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import threading
import time
from typing import Dict, List, Callable, Optional
import yfinance as yf

class RealTimeDataStream:
    """
    Real-time stock price streaming with fallback to polling
    """
    
    def __init__(self, symbols: List[str], update_interval: int = 5):
        """
        Initialize real-time data stream
        
        Args:
            symbols: List of stock symbols to track
            update_interval: Update interval in seconds (fallback for polling)
        """
        self.symbols = symbols
        self.update_interval = update_interval
        self.is_streaming = False
        self.callbacks = []
        self.current_data = {}
        self.websocket_url = None
        self.api_key = None
        
        # Fallback to Yahoo Finance polling
        self.use_polling = True  # Start with polling (free option)
        
    def add_callback(self, callback: Callable[[Dict], None]):
        """Add callback function for data updates"""
        self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[Dict], None]):
        """Remove callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            
    def _notify_callbacks(self, data: Dict):
        """Notify all registered callbacks with new data"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error: {e}")
                
    async def _websocket_stream(self):
        """WebSocket streaming (for premium APIs)"""
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                subscribe_msg = {
                    "action": "subscribe",
                    "symbols": self.symbols,
                    "apikey": self.api_key
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                while self.is_streaming:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        # Process and notify callbacks
                        processed_data = self._process_websocket_data(data)
                        if processed_data:
                            self._notify_callbacks(processed_data)
                            
                    except websockets.exceptions.ConnectionClosed:
                        break
                    except Exception as e:
                        print(f"WebSocket error: {e}")
                        break
                        
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
            # Fallback to polling
            self.use_polling = True
            
    def _process_websocket_data(self, data: Dict) -> Optional[Dict]:
        """Process WebSocket data into standardized format"""
        # This would depend on the specific API format
        # Example implementation:
        if 'symbol' in data and 'price' in data:
            return {
                'symbol': data['symbol'],
                'price': data['price'],
                'volume': data.get('volume', 0),
                'timestamp': datetime.now(),
                'change': data.get('change', 0),
                'change_percent': data.get('change_percent', 0)
            }
        return None
        
    def _polling_stream(self):
        """Fallback polling using Yahoo Finance"""
        while self.is_streaming:
            try:
                # Fetch current data for each symbol individually for better reliability
                for symbol in self.symbols:
                    try:
                        # Get recent data for this symbol
                        symbol_data = yf.download(
                            symbol,
                            period="5d",
                            interval="1m",
                            progress=False
                        )
                        
                        if not symbol_data.empty and len(symbol_data) > 1:
                            # Get the latest price - handle Series vs DataFrame
                            close_data = symbol_data['Close']
                            if isinstance(close_data, pd.Series):
                                current_price = close_data.iloc[-1]
                                prev_price = close_data.iloc[-2]
                            else:
                                current_price = close_data.iloc[-1, 0] if len(close_data.columns) > 0 else close_data.iloc[-1]
                                prev_price = close_data.iloc[-2, 0] if len(close_data.columns) > 0 else close_data.iloc[-2]
                            
                            # Calculate change
                            change = current_price - prev_price
                            change_percent = (change / prev_price * 100) if prev_price != 0 else 0
                            
                            # Get volume - handle Series vs DataFrame
                            volume_data = symbol_data['Volume']
                            if isinstance(volume_data, pd.Series):
                                volume = volume_data.iloc[-1]
                            else:
                                volume = volume_data.iloc[-1, 0] if len(volume_data.columns) > 0 else 0
                            
                            processed_data = {
                                'symbol': symbol,
                                'price': current_price,
                                'volume': volume,
                                'timestamp': datetime.now(),
                                'change': change,
                                'change_percent': change_percent
                            }
                            
                            self.current_data[symbol] = processed_data
                            self._notify_callbacks(processed_data)
                            
                    except Exception as symbol_error:
                        print(f"Error fetching data for {symbol}: {symbol_error}")
                        # Create placeholder data to show something is happening
                        if symbol not in self.current_data:
                            placeholder_data = {
                                'symbol': symbol,
                                'price': 0.0,
                                'volume': 0,
                                'timestamp': datetime.now(),
                                'change': 0.0,
                                'change_percent': 0.0,
                                'error': str(symbol_error)
                            }
                            self.current_data[symbol] = placeholder_data
                            self._notify_callbacks(placeholder_data)
                        
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(self.update_interval)
                
    def start_streaming(self):
        """Start real-time data streaming"""
        if self.is_streaming:
            return
            
        self.is_streaming = True
        
        if self.use_polling or not self.websocket_url:
            # Use polling (free option)
            self.polling_thread = threading.Thread(target=self._polling_stream)
            self.polling_thread.daemon = True
            self.polling_thread.start()
        else:
            # Use WebSocket (premium option)
            self.websocket_thread = threading.Thread(
                target=lambda: asyncio.run(self._websocket_stream())
            )
            self.websocket_thread.daemon = True
            self.websocket_thread.start()
            
    def stop_streaming(self):
        """Stop real-time data streaming"""
        self.is_streaming = False
        
    def get_current_data(self, symbol: str) -> Optional[Dict]:
        """Get current data for a specific symbol"""
        return self.current_data.get(symbol)
        
    def get_all_current_data(self) -> Dict:
        """Get current data for all symbols"""
        return self.current_data.copy()


class StreamlitRealTimeComponent:
    """
    Streamlit component for real-time data display
    """
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.stream = RealTimeDataStream(symbols)
        self.price_history = {symbol: [] for symbol in symbols}
        self.max_history = 100  # Keep last 100 price points
        
        # Register callback
        self.stream.add_callback(self._update_data)
        
    def _update_data(self, data: Dict):
        """Update data from stream"""
        symbol = data['symbol']
        if symbol in self.price_history:
            self.price_history[symbol].append({
                'price': data['price'],
                'timestamp': data['timestamp'],
                'change_percent': data['change_percent']
            })
            
            # Keep only recent history
            if len(self.price_history[symbol]) > self.max_history:
                self.price_history[symbol] = self.price_history[symbol][-self.max_history:]
                
    def render_dashboard(self):
        """Render real-time dashboard in Streamlit"""
        st.subheader("🔴 Live Market Data")
        
        # Start/stop controls
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Start Streaming", disabled=self.stream.is_streaming):
                self.stream.start_streaming()
                st.rerun()
                
        with col2:
            if st.button("Stop Streaming", not self.stream.is_streaming):
                self.stream.stop_streaming()
                st.rerun()
                
        # Display current data
        if self.stream.is_streaming:
            st.success("🟢 Streaming Active")
            
            # Check if we have any data
            current_data_all = self.stream.get_all_current_data()
            
            if not current_data_all:
                st.info("🔄 Initializing data feed... Please wait a moment.")
                st.spinner("Fetching market data...")
            else:
                # Create metrics for each symbol
                cols = st.columns(len(self.symbols))
                for i, symbol in enumerate(self.symbols):
                    with cols[i]:
                        current_data = self.stream.get_current_data(symbol)
                        if current_data and current_data['price'] > 0:
                            price = current_data['price']
                            change = current_data['change_percent']
                            
                            # Format currency based on market
                            if symbol.endswith('.NS'):
                                currency_symbol = "₹"
                            elif symbol.endswith(('.L', '.DE', '.SW', '.AS', '.PA')):
                                currency_symbol = "€"
                            else:
                                currency_symbol = "$"
                            
                            # Color coding
                            if change > 0:
                                st.metric(symbol, f"{currency_symbol}{price:.2f}", f"+{change:.2f}%", delta_color="normal")
                            elif change < 0:
                                st.metric(symbol, f"{currency_symbol}{price:.2f}", f"{change:.2f}%", delta_color="inverse")
                            else:
                                st.metric(symbol, f"{currency_symbol}{price:.2f}", "0.00%")
                        elif current_data and 'error' in current_data:
                            st.metric(symbol, "Error", "⚠️", help=current_data.get('error', 'Unknown error'))
                        else:
                            st.metric(symbol, "Loading...", "🔄")
                        
                # Display price charts
                st.subheader("Price Charts (Last 100 Updates)")
                for symbol in self.symbols:
                    if self.price_history[symbol]:
                        df = pd.DataFrame(self.price_history[symbol])
                        
                        st.write(f"**{symbol}**")
                        st.line_chart(df.set_index('timestamp')['price'])
                    else:
                        st.write(f"**{symbol}** - Waiting for data...")
                    
        else:
            st.warning("🔴 Streaming Stopped")
            st.info("Click 'Start Streaming' to begin real-time data updates")


# Example usage
if __name__ == "__main__":
    # Test real-time streaming
    symbols = ["RELIANCE.NS", "TCS.NS", "AAPL"]
    
    # Create streamlit component
    component = StreamlitRealTimeComponent(symbols)
    
    # In Streamlit app, call:
    # component.render_dashboard()
