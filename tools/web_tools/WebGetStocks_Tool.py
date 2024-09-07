import requests
import os
import sys
from bs4 import BeautifulSoup
from typing import Dict, Optional
import random
import time
import unittest
from unittest.mock import patch, Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.Base_Tool import Base_Tool

class WebGetStocks_Tool(Base_Tool):
    def execute(self, symbol: str) -> Optional[Dict[str, str]]:
        """
        Retrieves stock information for a given symbol from MarketWatch.

        Args:
        symbol (str): The stock symbol to look up.

        Returns:
        Optional[Dict[str, str]]: A dictionary containing the stock information, or None if an error occurs.
        """
        session = requests.Session()

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        ]

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.0",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            session.get("https://www.marketwatch.com/", headers=headers, timeout=10)
        except requests.RequestException as e:
            return self._handle_error(f"Error accessing MarketWatch home page: {str(e)}")

        time.sleep(random.uniform(1, 3))

        url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            intraday_element = soup.find('div', class_='element element--intraday')
            
            if not intraday_element:
                return self._handle_error(f"Could not find intraday element for {symbol}")
            
            stock_info = {
                'symbol': symbol.upper(),
                'last_price': self._safe_find(intraday_element, 'bg-quote', class_='value'),
                'change': self._safe_find(intraday_element, 'span', class_='change--point--q'),
                'change_percent': self._safe_find(intraday_element, 'span', class_='change--percent--q'),
                'volume': self._safe_find(intraday_element, 'span', class_='volume__value'),
                'last_updated': self._safe_find(intraday_element, 'span', class_='timestamp__time'),
                'close_price': self._safe_find(intraday_element, 'td', class_='table__cell u-semi'),
                'close_change': self._safe_find_nth(intraday_element, 'td', class_='table__cell', n=1),
                'close_change_percent': self._safe_find_nth(intraday_element, 'td', class_='table__cell', n=2)
            }
            
            # Remove any None values
            stock_info = {k: v for k, v in stock_info.items() if v is not None}
            
            return self._format_output(stock_info)
        
        except requests.RequestException as e:
            return self._handle_error(f"Error retrieving stock information for {symbol}: {str(e)}")

    def _safe_find(self, element, tag, class_=None, default='N/A'):
        """Safely find an element and return its text, or a default value if not found."""
        found = element.find(tag, class_=class_)
        return found.text.strip() if found else default

    def _safe_find_nth(self, element, tag, class_=None, n=0, default='N/A'):
        """Safely find the nth occurrence of an element and return its text, or a default value if not found."""
        found = element.find_all(tag, class_=class_)
        return found[n].text.strip() if len(found) > n else default

    def _validate_input(self, data: Dict[str, str]) -> Optional[str]:
        if 'symbol' not in data:
            return "Stock symbol is required."
        if not isinstance(data['symbol'], str) or len(data['symbol']) > 5:
            return "Invalid stock symbol format."
        return None

    def _format_output(self, result: Dict[str, str]) -> Dict[str, str]:
        return result  # The result is already in the desired format

    def _handle_error(self, error_message: str) -> Dict[str, str]:
        return {"error": error_message}

class TestWebGetStocksTool(unittest.TestCase):
    def setUp(self):
        self.tool = WebGetStocks_Tool()
        self.test_symbol = "AAPL"
        self.mock_html = """
        <div class="element element--intraday">
            <bg-quote class="value">150.00</bg-quote>
            <span class="change--point--q">+2.50</span>
            <span class="change--percent--q">+1.69%</span>
            <span class="volume__value">50,000,000</span>
            <span class="timestamp__time">4:00PM EDT</span>
            <td class="table__cell u-semi">147.50</td>
            <td class="table__cell">+2.50</td>
            <td class="table__cell">+1.69%</td>
        </div>
        """

    @patch('requests.Session')
    def test_successful_stock_retrieval(self, mock_session):
        mock_response = Mock()
        mock_response.text = self.mock_html
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.tool.execute(self.test_symbol)

        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['last_price'], '150.00')
        self.assertEqual(result['change'], '+2.50')
        self.assertEqual(result['change_percent'], '+1.69%')
        self.assertEqual(result['volume'], '50,000,000')

    @patch('requests.Session')
    def test_request_exception(self, mock_session):
        mock_session.return_value.get.side_effect = requests.RequestException("Connection error")

        result = self.tool.execute(self.test_symbol)

        self.assertIn('error', result)
        self.assertIn('Connection error', result['error'])

    @patch('requests.Session')
    def test_missing_intraday_element(self, mock_session):
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response

        result = self.tool.execute(self.test_symbol)

        self.assertIn('error', result)
        self.assertIn('Could not find intraday element', result['error'])

    def test_validate_input_valid(self):
        data = {"symbol": "AAPL"}
        result = self.tool._validate_input(data)
        self.assertIsNone(result)

    def test_validate_input_missing_symbol(self):
        data = {}
        result = self.tool._validate_input(data)
        self.assertEqual(result, "Stock symbol is required.")

    def test_validate_input_invalid_symbol(self):
        data = {"symbol": "TOOLONG"}
        result = self.tool._validate_input(data)
        self.assertEqual(result, "Invalid stock symbol format.")

    def test_safe_find(self):
        soup = BeautifulSoup(self.mock_html, 'html.parser')
        element = soup.find('div', class_='element element--intraday')
        result = self.tool._safe_find(element, 'bg-quote', class_='value')
        self.assertEqual(result, '150.00')

    def test_safe_find_nth(self):
        soup = BeautifulSoup(self.mock_html, 'html.parser')
        element = soup.find('div', class_='element element--intraday')
        result = self.tool._safe_find_nth(element, 'td', class_='table__cell', n=1)
        self.assertEqual(result, '+2.50')

    def test_format_output(self):
        input_data = {'symbol': 'AAPL', 'last_price': '150.00'}
        result = self.tool._format_output(input_data)
        self.assertEqual(result, input_data)

    def test_handle_error(self):
        error_message = "Test error"
        result = self.tool._handle_error(error_message)
        self.assertEqual(result, {"error": "Test error"})

def print_example_command():
    print("\nExample command line to run the WebGetStocks_Tool:")
    print("python tools/web_tools/WebGetStocks_Tool.py AAPL")
    print("\n\r Running tests on this tool...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If arguments are provided, do not run the tests
        symbol = sys.argv[1]
        tool = WebGetStocks_Tool()
        result = tool.execute(symbol)
        print(result)
    else:
        # If no arguments, run the tests
        print_example_command()
        unittest.main()
        
