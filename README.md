<h1>NBA Betting Best Bet Predictor</h1>

This project is a Python-based system designed to analyze NBA player statistics, pull daily betting odds, and recommend the best bets for a given day. It uses data from recent player performance and team defense rankings to determine the best over/under bets, and incorporates machine learning to predict bet success based on historical performance.

<h3>Features</h3>

<h4>Data Gathering:</h4>
Pulls all available NBA bets and betting odds for the day from APIs (Sportsradar, Balldontlie).
Retrieves relevant player statistics from their last 10 games for analysis.
Uses a web crawler with Selenium WebDriver to gather opposing team defense rankings.

<h4>Multithreading:</h4>
Efficiently gathers statistics for each bet using multithreading, employing a producer-consumer pattern.
Web crawling for defense rankings is parallelized for faster performance.

<h4>Bet Recommendation Algorithm:</h4>
Recommends "Over" bets when the player has exceeded the line in at least 70% of their recent games and averages higher than the betting line.
Recommends "Under" bets when the player is under the line in at least 70% of their recent games and averages lower than the betting line.

<h4>Machine Learning Prediction:</h4>
A decision tree machine learning model, implemented with scikit-learn, is trained on historical bets and performance.
Predicts the probability of success for each recommended bet based on gathered metrics and hit rates.

<h4>Post-Game Analysis:</h4>
Allows users to re-run the script in the evening to see which bets from the recommendations hit.

<h3>Installation</h3>
<h5>Prerequisites</h5>
- Python 3.x  <br />
- "requests" for API interaction  <br />
- "selenium" for web crawling  <br />
- "scikit-learn" for machine learning  <br />
- "threading" for multithreading functionality  <br />

<h6>Setup Selenium WebDriver</h6>
You need to have the appropriate WebDriver for your browser. For example, for Chrome:  <br />
Extract and place the chromedriver executable in your project directory or add it to your system PATH.  
