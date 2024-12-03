import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# Scrape Wikipedia using BeautifulSoup
def fetch_revenue_expenses():
    response = requests.get('https://en.wikipedia.org/wiki/Big_Ten_Conference')
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('table', {'class': 'wikitable'})
    table = tables[5]
    rows = table.find_all('tr')[1:]

    data = []
    profits = []
    colleges = []
    for row in rows:
        columns = row.find_all(['td', 'th'])
        college = columns[0].text.strip()
        revenue = columns[1].text.strip()
        expenses = columns[2].text.strip()

        revenue_clean = int(revenue.replace(',', '').replace('$', ''))
        expenses_clean = int(expenses.replace(',', '').replace('$', ''))

        netprofit = revenue_clean - expenses_clean

        profits.append(netprofit)
        colleges.append(college)
        formatted_netprofit = f"${netprofit:,.0f}"

        data.append([college, revenue, expenses, formatted_netprofit])
    
    return data, profits, colleges

def create_bar_chart(profits, colleges):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    ax.barh(colleges, [p / 1_000_000 for p in profits], color='skyblue')
    ax.set_xlabel('Net Profit ($) in Millions')
    
    # Set x axis labels to multiples of 10
    max_profit_in_millions = max(profits) / 1_000_000
    ticks = list(range(0, int(max_profit_in_millions) + 10, 10))
    
    ax.set_xticks(ticks)
    ax.set_xticklabels([f'{tick}M' for tick in ticks])
    ax.set_title('Net Profits of Big Ten Schools')
    plt.tight_layout()
    
    return fig

class RevenueExpenseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Big Ten Conference Revenue and Expenses')
        self.setGeometry(100, 200, 1100, 640)

        layout = QHBoxLayout()
        
        left_layout = QVBoxLayout()
        label = QLabel('Revenue and Expenses of Big Ten Conference:')
        left_layout.addWidget(label)

        self.table_widget = QTableWidget()
        left_layout.addWidget(self.table_widget)

        data, profits, colleges = fetch_revenue_expenses()

        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['College', 'Revenue', 'Expenses', 'Net Profit'])

        # Populate the table
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(value)))
                if j == 3: #highlighting
                    item = self.table_widget.item(i, j)
                    item.setBackground(QColor(144, 238, 144))

        chart_widget = FigureCanvas(create_bar_chart(profits, colleges))

        right_layout = QVBoxLayout()
        right_layout.addWidget(chart_widget)
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = RevenueExpenseWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
