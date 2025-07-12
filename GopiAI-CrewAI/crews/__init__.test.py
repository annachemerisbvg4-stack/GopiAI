import unittest

class Crew:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def __str__(self):
        return f"{self.name} ({self.role})"

class TestCrew(unittest.TestCase):

    def test_crew_creation(self):
        crew_member = Crew("Alice", "Captain")
        self.assertEqual(crew_member.name, "Alice")
        self.assertEqual(crew_member.role, "Captain")

    def test_crew_string_representation(self):
        crew_member = Crew("Bob", "Engineer")
        self.assertEqual(str(crew_member), "Bob (Engineer)")

    def test_crew_empty_name(self):
        crew_member = Crew("", "Pilot")
        self.assertEqual(crew_member.name, "")
        self.assertEqual(crew_member.role, "Pilot")

    def test_crew_special_characters(self):
        crew_member = Crew("C@rl", "Medic!")
        self.assertEqual(crew_member.name, "C@rl")
        self.assertEqual(crew_member.role, "Medic!")

    def test_crew_unicode_name(self):
        crew_member = Crew("Björn", "Navigator")
        self.assertEqual(crew_member.name, "Björn")
        self.assertEqual(crew_member.role, "Navigator")