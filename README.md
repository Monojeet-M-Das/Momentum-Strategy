
🚀 Momentum-Based Portfolio Strategy with Backtrader

This project implements and backtests a momentum-based portfolio trading strategy using the Backtrader framework and yfinance data. The strategy ranks stocks in the S&P 500 by their momentum, and dynamically allocates capital to the top-performing ones while avoiding those below long-term trend lines or underperforming the market.

📌 Strategy Overview
✅ Core Logic

    Momentum Signal: Calculated using a linear regression slope of log returns over a 90-day window, annualized and adjusted by R².

    Rebalancing:

        Every week: Re-rank stocks and open/close long positions in the top 20% by momentum.

        Every two weeks: Adjust position sizes to target ATR-based volatility allocation.

    Market Filter: Long positions are only opened when the S&P 500 index is above its 200-day SMA.

    Risk Control:

        Position sizing based on ATR(20)

        Ignore stocks with less than 100 days of data

📦 Requirements

pip install yfinance backtrader scipy numpy pandas matplotlib

📂 Files

    Momentum_Trading_Strategy_implementation.py
    Complete implementation of the strategy including:

        Custom momentum indicator

        Dynamic rebalancing logic

        Risk-adjusted sizing using ATR

        Analyzer metrics for performance evaluation

    companies_all
    A local file (assumed to be .txt) containing ticker symbols, one per line.
    Make sure to update the file path in the script:

    with open('companies_all') as file_in:

▶️ How to Run

    Update the path to the companies_all file with your local list of stock tickers.

    Then run:

python Momentum_Trading_Strategy_implementation.py

📈 Example Output

initial capital: $100000.00
Sharpe ratio: 1.21
Return: 85.32%
Max Drawdown: 14.27%
Capital: $185320.50

📊 Key Indicators Used
Indicator	Purpose
Momentum (custom)	Stock ranking
SMA(100)	Stock-level trend filter
SMA(200)	S&P 500 trend filter
ATR(20)	Position sizing
📜 License

This project is under the MIT License.
🙏 Acknowledgements

    Backtrader – Python backtesting library

    Yahoo Finance via yfinance – Historical data source

    Strategy inspired by academic and practitioner literature on momentum investing.
