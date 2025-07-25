import pandas as pd
import numpy as np
import os

# Ensure output folder exists
os.makedirs("datasets", exist_ok=True)

# 1. Sales Data
np.random.seed(0)
sales_data = pd.DataFrame({
    "Region": np.random.choice(["North", "South", "East", "West"], 200),
    "Product": np.random.choice(["Laptop", "Tablet", "Smartphone", "Monitor"], 200),
    "Units Sold": np.random.poisson(30, 200),
    "Unit Price": np.random.uniform(100, 1000, 200).round(2)
})
sales_data["Total Sales"] = (sales_data["Units Sold"] * sales_data["Unit Price"]).round(2)
sales_data.to_csv("datasets/sales_data.csv", index=False)

# 2. Employee Data
employee_data = pd.DataFrame({
    "Department": np.random.choice(["HR", "Engineering", "Marketing", "Finance"], 150),
    "Gender": np.random.choice(["Male", "Female"], 150),
    "Experience (Years)": np.random.randint(1, 21, 150),
    "Salary": np.random.normal(70000, 15000, 150).astype(int)
})
employee_data.to_csv("datasets/employee_data.csv", index=False)

# 3. Student Scores
study_hours = np.random.uniform(0, 10, 100)
sleep_hours = np.random.uniform(4, 9, 100)
test_score = 3.5 * study_hours + 2 * sleep_hours + np.random.normal(0, 3, 100)
student_data = pd.DataFrame({
    "Study Hours": study_hours.round(2),
    "Sleep Hours": sleep_hours.round(2),
    "Test Score": test_score.round(2)
})
student_data.to_csv("datasets/student_scores.csv", index=False)

# 4. E-Commerce User Behavior
ecommerce_data = pd.DataFrame({
    "User ID": np.arange(1000, 1100),
    "Age": np.random.randint(18, 60, 100),
    "Session Time (min)": np.random.normal(12, 5, 100).round(2),
    "Page Views": np.random.poisson(6, 100)
})
ecommerce_data.to_csv("datasets/ecommerce_data.csv", index=False)

# 5. Marketing Campaign
campaign_data = pd.DataFrame({
    "Campaign": np.random.choice(["A", "B", "C", "D"], 120),
    "Channel": np.random.choice(["Email", "Social Media", "Ads", "Referral"], 120),
    "Spend ($)": np.random.uniform(500, 10000, 120).round(2),
    "ROI (%)": np.random.normal(12, 4, 120).round(2)
})
campaign_data.to_csv("datasets/marketing_campaign.csv", index=False)

# 6. Web traffic dummy dataset

dates = pd.date_range(start="2024-01-01", end="2024-06-30", freq="D")
sessions = np.random.poisson(150, len(dates))
page_views = sessions * np.random.uniform(1.2, 1.8, len(dates))
bounce_rate = np.random.uniform(30, 70, len(dates))

df = pd.DataFrame({
    "Date": dates,
    "Sessions": sessions,
    "Page Views": page_views.round(0).astype(int),
    "Bounce Rate (%)": bounce_rate.round(2)
})
df.to_csv("datasets/web_traffic.csv", index=False)

print("✅ All datasets generated in /datasets")
