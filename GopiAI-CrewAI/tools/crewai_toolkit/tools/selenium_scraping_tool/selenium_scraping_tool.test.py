import unittest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from crewai.tools.selenium_scrape import (
    SeleniumScrapingTool,
    SeleniumScrapingToolSchema,
)


class TestSeleniumScrapingToolSchema(unittest.TestCase):
    def test_valid_schema(self):
        data = {"website_url": "https://www.example.com", "css_element": "div"}
        schema = SeleniumScrapingToolSchema(**data)
        self.assertEqual(schema.website_url, "https://www.example.com")
        self.assertEqual(schema.css_element, "div")

    def test_invalid_url(self):
        with self.assertRaises(ValidationError):
            SeleniumScrapingToolSchema(website_url="invalid_url", css_element="div")

    def test_empty_url(self):
        with self.assertRaises(ValidationError):
            SeleniumScrapingToolSchema(website_url="", css_element="div")


class TestSeleniumScrapingTool(unittest.TestCase):
    @patch("crewai.tools.selenium_scrape.webdriver.Chrome")
    def test_run_method(self, mock_chrome):
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_element.text = "Test Content"
        mock_driver.find_elements.return_value = [mock_element]
        mock_chrome.return_value = mock_driver

        tool = SeleniumScrapingTool(driver=mock_driver)
        result = tool._run(website_url="https://www.example.com", css_element="div")

        self.assertEqual(result, "Test Content")

    @patch("crewai.tools.selenium_scrape.webdriver.Chrome")
    def test_run_method_exception(self, mock_chrome):
        mock_driver = MagicMock()
        mock_driver.get.side_effect = Exception("Simulated error")
        mock_chrome.return_value = mock_driver

        tool = SeleniumScrapingTool(driver=mock_driver)
        result = tool._run(website_url="https://www.example.com", css_element="div")

        self.assertIn("Error scraping website", result)

    @patch("crewai.tools.selenium_scrape.webdriver.Chrome")
    def test_make_request_invalid_url(self, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        tool = SeleniumScrapingTool(driver=mock_driver)

        with self.assertRaises(ValueError):
            tool._make_request("invalid_url", None, 1)