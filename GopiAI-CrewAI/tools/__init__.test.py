import unittest

def is_palindrome(text):
    processed_text = ''.join(filter(str.isalnum, text)).lower()
    return processed_text == processed_text[::-1]

def reverse_string(s):
    return s[::-1]

class TestTools(unittest.TestCase):

    def test_is_palindrome_valid(self):
        self.assertTrue(is_palindrome("madam"))

    def test_is_palindrome_invalid(self):
        self.assertFalse(is_palindrome("hello"))

    def test_is_palindrome_with_spaces(self):
        self.assertTrue(is_palindrome("race car"))

    def test_reverse_string_valid(self):
        self.assertEqual(reverse_string("abc"), "cba")

    def test_reverse_string_empty(self):
        self.assertEqual(reverse_string(""), "")