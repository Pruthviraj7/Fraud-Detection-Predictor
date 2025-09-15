import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: #7a694d;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .input-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .prediction-card {
        text-align: center;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .safe-transaction {
        background: grey;
        color: white;
    }
    
    .fraud-transaction {
        background: black;
        color: white;
    }
    
    .info-box {
        background: black;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: black;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load model (with error handling)
@st.cache_resource
def load_fraud_model():
    try:
        model = joblib.load("fraud_detection_model.pkl")
        return model
    except FileNotFoundError:
        st.error("⚠️ Model file 'fraud_detection_model.pkl' not found. Please ensure the model file is in the correct directory.")
        return None

model = load_fraud_model()

# Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ Fraud Detection System</h1>
    <p>Monitor unusual activities and keep your account secure.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
      
    st.markdown("### 📊 System Information")
    st.info("This system uses machine learning to analyze transaction patterns and detect potential fraud.")
    
    st.markdown("### 🔍 How it Works")
    st.markdown("""
    1. **Input Transaction Details** - Enter transaction information
    2. **AI Analysis** - Our model analyzes patterns
    3. **Risk Assessment** - Get instant fraud probability
    4. **Decision Support** - Receive actionable insights
    """)
    
    st.markdown("### ⚡ Transaction Types")
    st.markdown("""
    - **PAYMENT**: Regular payments
    - **TRANSFER**: Money transfers
    - **CASH_OUT**: Cash withdrawals
    - **DEPOSIT**: Account deposits
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💳 Transaction Details")
    
    # Input form in a styled container
    with st.container():
        # st.markdown('<div class="input-section">', unsafe_allow_html=True)
        
        # Transaction type with icons
        transaction_icons = {
            "PAYMENT": "💳",
            "TRANSFER": "↔️",
            "CASH_OUT": "💸",
            "DEPOSIT": "💰"
        }
        
        transaction_type = st.selectbox(
            "🏷️ Transaction Type",
            ["PAYMENT", "TRANSFER", "CASH_OUT", "DEPOSIT"],
            format_func=lambda x: f"{transaction_icons[x]} {x}",
            help="Select the type of transaction being processed"
        )
        
        # Amount input with better formatting
        amount = st.number_input(
            "💵 Transaction Amount ($)",
            min_value=0.0,
            value=100.0,
            step=10.0,
            format="%.2f",
            help="Enter the transaction amount in USD"
        )
        
        # Create two columns for sender and receiver details
        sender_col, receiver_col = st.columns(2)
        
        with sender_col:
            st.markdown("#### 👤 Sender Account")
            oldbalanceOrg = st.number_input(
                "Previous Balance ($)",
                min_value=0.0,
                value=10000.0,
                step=100.0,
                format="%.2f",
                key="sender_old"
            )
            newbalanceOrig = st.number_input(
                "New Balance ($)",
                min_value=0.0,
                value=9000.0,
                step=100.0,
                format="%.2f",
                key="sender_new"
            )
        
        with receiver_col:
            st.markdown("#### 👥 Receiver Account")
            oldbalanceDest = st.number_input(
                "Previous Balance ($)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="receiver_old"
            )
            newbalanceDest = st.number_input(
                "New Balance ($)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="receiver_new"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Balance validation
        sender_diff = oldbalanceOrg - newbalanceOrig
        receiver_diff = newbalanceDest - oldbalanceDest
        
        if abs(sender_diff - amount) > 0.01 and transaction_type in ["PAYMENT", "TRANSFER"]:
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>Balance Mismatch Warning:</strong> The sender's balance change doesn't match the transaction amount. This might indicate suspicious activity.
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📈 Transaction Summary")
    
    # Display transaction summary
    st.markdown(f"""
    <div class="metric-card">
        <h4>💳 {transaction_icons[transaction_type]} {transaction_type}</h4>
        <h2>${amount:,.2f}</h2>
        <p>Transaction Amount</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Balance changes
    st.markdown("#### 📊 Account Changes")
    
    col_sender, col_receiver = st.columns(2)
    with col_sender:
        st.metric(
            "Sender Balance",
            f"${newbalanceOrig:,.2f}",
            f"-${sender_diff:,.2f}" if sender_diff > 0 else f"+${abs(sender_diff):,.2f}"
        )
    
    with col_receiver:
        st.metric(
            "Receiver Balance",
            f"${newbalanceDest:,.2f}",
            f"+${receiver_diff:,.2f}" if receiver_diff > 0 else f"-${abs(receiver_diff):,.2f}"
        )

# Prediction button and results
st.markdown("---")

col_predict, col_space = st.columns([1, 2])
with col_predict:
    predict_button = st.button("🔍 Analyze Transaction", type="primary", use_container_width=True)

if predict_button and model is not None:
    # Prepare input data
    input_data = pd.DataFrame({
        "type": [transaction_type],
        "amount": [amount],
        "oldbalanceOrg": [oldbalanceOrg],
        "newbalanceOrig": [newbalanceOrig],
        "oldbalanceDest": [oldbalanceDest],
        "newbalanceDest": [newbalanceDest]
    })
    
    try:
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        # Get prediction probability if available
        try:
            prediction_proba = model.predict_proba(input_data)[0]
            fraud_probability = prediction_proba[1] * 100
        except:
            fraud_probability = None
        
        # Display results
        col_result1, col_result2 = st.columns(2)
        
        with col_result1:
            if prediction == 1:
                st.markdown(f"""
                <div class="prediction-card fraud-transaction">
                    <h2>⚠️ FRAUD DETECTED</h2>
                    <h3>High Risk Transaction</h3>
                    <p>This transaction shows patterns consistent with fraudulent activity.</p>
                    {"<p><strong>Fraud Probability: {:.1f}%</strong></p>".format(fraud_probability) if fraud_probability else ""}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="warning-box">
                    <strong>🚨 Recommended Actions:</strong>
                    <ul>
                        <li>Block the transaction immediately</li>
                        <li>Contact the account holder for verification</li>
                        <li>Flag account for manual review</li>
                        <li>Document incident for compliance</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.markdown(f"""
                <div class="prediction-card safe-transaction">
                    <h2>✅ TRANSACTION APPROVED</h2>
                    <h3>Low Risk Transaction</h3>
                    <p>This transaction appears to be legitimate and safe to process.</p>
                    {"<p><strong>Fraud Probability: {:.1f}%</strong></p>".format(fraud_probability) if fraud_probability else ""}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="info-box">
                    <strong>✅ Transaction Status:</strong>
                    <ul>
                        <li>Transaction patterns are normal</li>
                        <li>Safe to process</li>
                        <li>Continue standard monitoring</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        with col_result2:
            # Risk factors visualization
            if fraud_probability is not None:
                # Create a gauge chart for fraud probability
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = fraud_probability,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Fraud Risk Score"},
                    delta = {'reference': 50},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 25], 'color': "lightgreen"},
                            {'range': [25, 75], 'color': "yellow"},
                            {'range': [75, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Risk factors analysis
            st.markdown("#### 🔍 Risk Factors")
            risk_factors = []
            
            if amount > 50000:
                risk_factors.append("High transaction amount")
            if transaction_type in ["CASH_OUT", "TRANSFER"]:
                risk_factors.append("High-risk transaction type")
            if oldbalanceOrg == 0:
                risk_factors.append("Zero sender balance")
            if abs(sender_diff - amount) > 0.01:
                risk_factors.append("Balance inconsistency")
            
            if risk_factors:
                for factor in risk_factors:
                    st.warning(f"⚠️ {factor}")
            else:
                st.success("✅ No significant risk factors detected")
                
    except Exception as e:
        st.error(f"❌ Prediction error: {str(e)}")

elif predict_button and model is None:
    st.error("❌ Cannot make prediction without a valid model file.")

# Footer with additional information
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>🛡️ Fraud Detection System</strong></p>
    <p>Smart analysis for safer transactions</p>
</div>
""", unsafe_allow_html=True)
