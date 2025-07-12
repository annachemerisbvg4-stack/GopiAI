import unittest

def is_palindrome(s):
  """Checks if a string is a palindrome (reads the same forwards and backward)."""
  s = s.lower()
  s = ''.join(filter(str.isalnum, s))
  return s == s[::-1]

class TestPalindrome(unittest.TestCase):

    def test_empty_string(self):
        self.assertTrue(is_palindrome(""))

    def test_simple_palindrome(self):
        self.assertTrue(is_palindrome("madam"))

    def test_non_palindrome(self):
        self.assertFalse(is_palindrome("hello"))

    def test_palindrome_with_spaces(self):
        self.assertTrue(is_palindrome("race car"))

    def test_palindrome_with_punctuation(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))

if __name__ == '__main__':
    unittest.main()