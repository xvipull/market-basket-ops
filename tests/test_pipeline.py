import tempfile
import unittest
from pathlib import Path

from src.pipeline import QualityError, standardize, validate


class PipelineTests(unittest.TestCase):
    def test_standardize_normalizes_keys_currency_and_category(self):
        rows = standardize("products", [{"sku_id": " sku-1 ", "product_name": "  Bread ", "category": "bakery", "unit_cost": "10", "active_flag": "y"}])
        self.assertEqual(rows[0]["sku_id"], "SKU-1")
        self.assertEqual(rows[0]["category"], "Bakery")
        self.assertEqual(rows[0]["unit_cost"], "10.00")

    def test_invalid_inventory_range_fails_validation(self):
        datasets = {
            "products": [{"sku_id":"SKU-1","product_name":"Item","category":"Test","unit_cost":"1.00","active_flag":"Y"}],
            "stores": [{"store_id":"S1","store_name":"Store","store_cluster":"Test","city":"Mumbai","active_flag":"Y"}],
            "transactions": [{"transaction_id":"T1","line_number":"1","transaction_ts":"2026-09-15T10:00:00+05:30","store_id":"S1","sku_id":"SKU-1","quantity":"1","unit_price":"10.00","discount_amount":"0.00","currency":"INR","status":"COMPLETED"}],
            "inventory": [{"inventory_date":"2026-09-15","store_id":"S1","sku_id":"SKU-1","on_hand_qty":"-1","in_stock_flag":"Y"}],
            "promotions": [{"promotion_id":"P1","promotion_name":"Test","start_date":"2026-09-15","end_date":"2026-09-16","sku_id":"SKU-1","store_id":"S1","discount_type":"AMOUNT_OFF"}],
        }
        with self.assertRaises(QualityError):
            validate(datasets)


if __name__ == "__main__":
    unittest.main()
