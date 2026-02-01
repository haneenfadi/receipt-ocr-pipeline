## OCR Evaluation Results
```
{
  "total_receipts": 7,
  "store_name_accuracy": "85.7%",
  "receipt_number_accuracy": "100.0%",
  "date_accuracy": "100.0%",
  "currency_accuracy": "100.0%",
  "item_name_accuracy": "94.0%",
  "quantity_accuracy": "100.0%",
  "taxes_accuracy": "85.7%",
  "total_amount_accuracy": "100.0%"
}
```
## Detailed Errors Per Image
```
[
  {
    "image": "ar_image(3).jpg",
    "errors": {
      "taxes": {
        "gt": null,
        "pred": "0"
      },
      "items": [
        {
          "index": 0,
          "field": "item_name",
          "gt": "س فول-بالصلصة",
          "pred": "من فول-بالصلصة"
        },
        {
          "index": 1,
          "field": "item_name",
          "gt": " س بطاطس-شيبسي",
          "pred": "من بطاطس-شيبسي"
        }
      ]
    }
  },
  {
    "image": "ar_image(4).png",
    "errors": {
      "store_name": {
        "gt": "حلواني العبد",
        "pred": null
      }
    }
  },
  {
    "image": "ar_image(5).jpg",
    "errors": {
      "items": [
        {
          "index": 1,
          "field": "item_name",
          "gt": "كفته كندوز",
          "pred": "كفاه كدرر"
        },
        {
          "index": 3,
          "field": "item_name",
          "gt": "ممبار",
          "pred": "ممبر"
        }
      ]
    }
  },
  {
    "image": "ar_image(6).jpg",
    "errors": {
      "items": [
        {
          "index": 0,
          "field": "item_name",
          "gt": "علبة كينج",
          "pred": "علبه كيلج"
        }
      ]
    }
  }
]
```
