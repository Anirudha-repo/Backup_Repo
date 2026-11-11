import pandas as pd
import numpy as np

df["UnitPrice"] = df["UnitPrice"].fillna(groupby("Category")["UnitPrice"].mean()) 


df["Sales"] = df.drop_duplicates(subset=["Sales"])

df["CustomerType"] = df["CustomerType"].replace(
    {
        "Regular" : "R"
        "Member" : "M"
    }
)

merge = df.merge("Sales Data","Product Master",on="ProductID",how="inner")
merge["TotalSaleAmount"] = df["UnitPrice"] * df["QuantitySold"]

