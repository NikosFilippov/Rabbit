import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
sales = pd.DataFrame({
    "product": ["coffee", "kanelsnegl", "rugbrød", "coffee", "tea"],
    "price":   [25.0, 22.5, 45.0, 25.0, 20.0],
    "units":   [84, 37, 12, 91, 18],
})

sales["revenue"] = sales["price"] * sales["units"]   # 1. add a column "revenue" = price * units


busy = sales[sales["units"]>50]   # 2. keep only the rows with more than 50 units sold, call it busy


total_revenue = sales["revenue"].sum()    # 3. put the total revenue in total_revenue


assert "revenue" in sales.columns, "step 1: add the revenue column"
assert len(busy) == 2, "step 2: two rows sold more than 50 units"
assert round(total_revenue, 2) == 6107.50, "step 3: sum the revenue column"
print(f"All correct. Total revenue: {total_revenue:.2f} kr")
x=sales["product"]
y = sales["revenue"]
plt.barh(x,y); # your plot here)
plt.title("Revenue by Product")
plt.show()