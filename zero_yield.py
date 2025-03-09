import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import interp1d  # For smooth curve

# Step 1: Define function to compute zero-coupon bond value
def zcb_value(F, r, T, freq=1):
    n = T * freq
    dr = r / freq
    val = F / (1 + dr) ** n
    return val

# Step 2: Extract zero rates from bond dataset
def extract_rates(df):
    zr = {}
    df = df.sort_values('T')  # Sort by maturity
    
    for _, row in df.iterrows():
        T = row['T']
        c = row['c'] / 100  # Convert coupon to decimal
        P = row['P']
        FV = row['FV']
        n = int(T * 2)  # Semi-annual periods
        cp = (c * FV) / 2  # Coupon payment
        
        if n == 1:  # Single period bond
            rate = 2 * ((FV + cp) / P - 1)
            zr[T] = rate
        else:
            # Compute present value of known cash flows
            cf = [cp] * (n - 1) + [cp + FV]
            pv = 0
            for i in range(1, n):
                t = i / 2
                if t in zr:
                    pv += cf[i-1] / (1 + zr[t]/2) ** i
            
            # Solve for current maturity's rate
            rem = P - pv
            rate = 2 * ((cf[-1] / rem) ** (1/n) - 1)
            zr[T] = rate
    
    return zr

# Step 3: Execute examples and visualize
def run():
    # Example 1: Zero-coupon bond
    F = 1000
    r = 0.05
    T = 2
    val = zcb_value(F, r, T)
    print(f"ZCB Value: ${val:.2f}")
    
    # Example 2: Zero rates from bond data
    df = pd.DataFrame({
        'T': [0.5, 1.0, 1.5, 2.0],
        'c': [4.0, 4.5, 5.0, 5.5],
        'P': [99.50, 99.00, 98.50, 98.00],
        'FV': [100, 100, 100, 100]
    })
    
    zr = extract_rates(df)
    print("\nExtracted Zero Rates:")
    for t, r in zr.items():
        print(f"Time {t} years: {r*100:.2f}%")
    
    # Step 4: Plot using Plotly
    fig = go.Figure()
    XX = list(zr.keys())
    YY = [r * 100 for r in zr.values()]
    
    # Raw data points
    fig.add_trace(go.Scatter(
        x=XX, y=YY, mode='markers', name='Zero Rates',
        marker=dict(color='#FF6B6B', size=10),
        text=[f'Maturity: {x:.1f}y<br>Rate: {y:.2f}%' for x, y in zip(XX, YY)],
        hoverinfo='text'
    ))
    
    # Interpolated curve
    f = interp1d(XX, YY, kind='cubic', fill_value="extrapolate")
    X_smooth = np.linspace(min(XX), max(XX), 100)
    Y_smooth = f(X_smooth)
    fig.add_trace(go.Scatter(
        x=X_smooth, y=Y_smooth, mode='lines', name='Yield Curve',
        line=dict(color='#4ECDC4', width=2)
    ))
    
    fig.update_layout(
        title=dict(text='Zero Yield Curve from Bond Data', font=dict(color='white', size=16)),
        xaxis_title=dict(text='Maturity (Years)', font=dict(color='white', size=12)),
        yaxis_title=dict(text='Zero Rate (%)', font=dict(color='white', size=12)),
        plot_bgcolor='rgb(40, 40, 40)',
        paper_bgcolor='rgb(40, 40, 40)',
        font=dict(color='white'),
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', gridwidth=1, zeroline=False),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.2)', gridwidth=1, zeroline=False),
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(50, 50, 50, 0.8)')
    )
    
    fig.show()

if __name__ == "__main__":
    run()
