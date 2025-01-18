import math
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.stats import norm
from flask import Flask, send_file

# Flask app setup
app = Flask(__name__)

# Function to calculate ITM probability
def calculate_itm_probability(S, K, T, r, sigma, option_type='call'):
    if T == 0:  # Handle expiration day separately
        if option_type == 'call':
            return 100 if S >= K else 0  # Call: 100% if ITM, otherwise 0%
        elif option_type == 'put':
            return 100 if S <= K else 0  # Put: 100% if ITM, otherwise 0%
        else:
            raise ValueError("Invalid option type. Use 'call' or 'put'.")
    # Black-Scholes formula for ITM probability
    d2 = (math.log(S / K) + (r - 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    if option_type == 'call':
        return norm.cdf(d2) * 100  # Convert to percentage
    elif option_type == 'put':
        return (1 - norm.cdf(d2)) * 100  # Convert to percentage

# Animation Function
def create_animation(output_file="animation.gif"):
    # Parameters
    S = 23100        # Current stock price
    r = 0.03         # Risk-free interest rate
    sigma = 0.2      # Volatility (20%)
    strike_prices = range(22000, 24001, 500)  # Range of strike prices (22000 to 24000)
    days_in_month = 30  # Total days to expiration

    # Prepare figure
    fig, ax = plt.subplots(figsize=(12, 8))
    lines = {}
    annotations = {}
    day_labels = []  # Store day number annotations
    for K in strike_prices:
        lines[K] = {
            'call': ax.plot([], [], label=f'Call ITM (K={K})', linestyle='-', marker='o')[0],
            'put': ax.plot([], [], label=f'Put ITM (K={K})', linestyle='--', marker='o')[0],
        }
        annotations[K] = {
            'call': [],
            'put': [],
        }

    # Setup axes
    ax.set_xlim(0, days_in_month)
    ax.set_ylim(0, 100)
    ax.set_title('Dynamic ITM Probability vs. Days to Expiration')
    ax.set_xlabel('Days to Expiration')
    ax.set_ylabel('ITM Probability (%)')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid()

    # Animation function
    def animate(day):
        T = (days_in_month - day) / 365  # Time to expiration in years
        x = list(range(day + 1))  # X-axis for the days

        # Clear previous annotations
        for K in strike_prices:
            for annotation in annotations[K]['call'] + annotations[K]['put']:
                annotation.remove()
            annotations[K]['call'].clear()
            annotations[K]['put'].clear()

        # Clear previous day labels
        for label in day_labels:
            label.remove()
        day_labels.clear()

        for K in strike_prices:
            # Calculate ITM probabilities dynamically
            call_probs = [calculate_itm_probability(S, K, (days_in_month - d) / 365, r, sigma, 'call') for d in x]
            put_probs = [calculate_itm_probability(S, K, (days_in_month - d) / 365, r, sigma, 'put') for d in x]

            # Update line data
            lines[K]['call'].set_data(x, call_probs)
            lines[K]['put'].set_data(x, put_probs)

            # Annotate percentages
            annotations[K]['call'].append(ax.annotate(f"{call_probs[-1]:.1f}%", (x[-1], call_probs[-1]),
                                                      textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8, color='blue'))
            annotations[K]['put'].append(ax.annotate(f"{put_probs[-1]:.1f}%", (x[-1], put_probs[-1]),
                                                     textcoords="offset points", xytext=(0, -10), ha='center', fontsize=8, color='red'))

        # Annotate the current day on the graph
        day_label = ax.annotate(f"Day {day}", (x[-1], 5), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=12, color='black', weight='bold')
        day_labels.append(day_label)

        return [line['call'] for line in lines.values()] + [line['put'] for line in lines.values()] + day_labels

    # Create the animation
    ani = FuncAnimation(fig, animate, frames=days_in_month + 1, interval=200, blit=False)
    ani.save(output_file, writer="imagemagick")  # Save the animation as a GIF
    print(f"Animation saved as {output_file}")

# Flask route to serve the animation
@app.route("/")
def serve_animation():
    if not os.path.exists("animation.gif"):
        create_animation("animation.gif")  # Generate the animation if it doesn't exist
    return send_file("animation.gif", mimetype="image/gif")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment variable
    app.run(host="0.0.0.0", port=port)
