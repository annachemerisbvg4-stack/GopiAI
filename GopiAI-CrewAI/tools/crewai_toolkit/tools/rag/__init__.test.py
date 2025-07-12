import unittest

def is_palindrome(text):
  """
  Checks if a given string is a palindrome (reads the same forwards and backward).
  Ignores case and non-alphanumeric characters.
  """
  processed_text = ''.join(filter(str.isalnum, text)).lower()
  return processed_text == processed_text[::-1]

class TestPalindrome(unittest.TestCase):

    def test_empty_string(self):
        self.assertTrue(is_palindrome(""))

    def test_simple_palindrome(self):
        self.assertTrue(is_palindrome("madam"))

    def test_non_palindrome(self):
        self.assertFalse(is_palindrome("hello"))

    def test_palindrome_with_spaces_and_case(self):
        self.assertTrue(is_palindrome("Race car"))

    def test_palindrome_with_punctuation(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))