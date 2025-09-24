# Phase 2 - Exploratory Data Analysis (EDA)

This phase performs comprehensive exploratory data analysis on the Air Quality UCI dataset to understand temporal patterns, correlations, and data characteristics that will inform the predictive modeling in Phase 3.

## Prerequisites

1. Ensure you have completed Phase 1 (Kafka streaming infrastructure)
2. Make sure you have a Python virtual environment activated with required packages installed:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the [Air Quality UCI dataset](https://archive.ics.uci.edu/dataset/360/air+quality) is available at `src/data/AirQualityUCI.csv`

## Running the EDA Notebook

1. Navigate to the src directory:

   ```bash
   cd src
   ```

2. Start Jupyter Notebook:

   ```bash
   jupyter notebook phase_2_eda.ipynb
   ```

3. Run all cells by selecting "Cell" → "Run All" from the menu, or use the keyboard shortcut `Shift + Enter` to run cells individually.

## Expected Outputs

After running all cells, you will have:

**Data Files:**

- `data/train.csv` - Training dataset (80% of data)
- `data/test.csv` - Test dataset (20% of data)

**Visualization Artifacts in `artifacts/` folder:**

- Time series plots for major pollutants
- Hourly and weekly operational pattern charts
- ACF and PACF plots for temporal dependency analysis
- Seasonal decomposition charts

**Key Insights Generated:**

- Understanding of daily and weekly pollution cycles
- Correlation patterns between pollutants and environmental factors
- Identification of temporal dependencies for model selection
- Data quality assessment for feature engineering decisions
