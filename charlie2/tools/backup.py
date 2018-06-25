import pickle
from PyQt5.QtWidgets import QTableWidgetItem
from .paths import pickles


def _populate_table(table):
    """Fill a table"""
    all_data = [pickle.load(f) for f in pickles]
    all_keys = {k for dic in all_data for k in dic}
    for row, dic in enumerate(all_data):
        for col, key in all_keys:
            if key in dic:
                item = dic[key]
                if not isinstance(item, (str, int, float, bool)):
                    try:
                        str(item)
                    except:
                        pass
                item = QTableWidgetItem(item)
                table.setItem(row, col, item)

