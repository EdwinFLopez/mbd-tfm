import pandas as pd


def get_data(query: str) -> pd.DataFrame:
    return __dummy_data__()

def get_recommendations(sku: str) -> pd.DataFrame:
    return __dummy_data__()

def __dummy_data__() -> pd.DataFrame:
    return pd.DataFrame({
        "product_sku": ["24-MB04", "24-MB05", "24-MB05"],
        "product_name": ["Red Shoes", "Blue Hat", "Green Shirt"],
        "product_properties": [
            "{\"product_sku\":\"24-MB04\",\"product_type\":\"simple\",\"product_ratings\":4.5000,\"product_categories\":[\"Gear\",\"Collections\"],\"product_ratings_pct\":90.0000,\"product_attribute_set\":\"Bag\"}",
            "{\"product_sku\":\"24-MB05\",\"product_type\":\"simple\",\"product_ratings\":4.5000,\"product_categories\":[\"Gear\",\"Collections\"],\"product_ratings_pct\":90.0000,\"product_attribute_set\":\"Bag\"}",
            "{\"product_sku\":\"24-MB06\",\"product_type\":\"simple\",\"product_ratings\":4.5000,\"product_categories\":[\"Gear\",\"Collections\"],\"product_ratings_pct\":90.0000,\"product_attribute_set\":\"Bag\"}"
        ]
    })