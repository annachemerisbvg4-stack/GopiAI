import unittest
from unittest.mock import patch

# Assume the crew module has a Crew class and related functions
# For example:
class Crew:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def __str__(self):
        return f"{self.name} ({self.role})"

def create_crew_member(name, role):
    return Crew(name, role)

def list_crew(crew_list):
    return [str(member) for member in crew_list]


class TestCrew(unittest.TestCase):

    def test_create_crew_member(self):
        crew_member = create_crew_member("Alice", "Pilot")
        self.assertEqual(crew_member.name, "Alice")
        self.assertEqual(crew_member.role, "Pilot")

    def test_crew_member_string_representation(self):
        crew_member = Crew("Bob", "Engineer")
        self.assertEqual(str(crew_member), "Bob (Engineer)")

    def test_list_crew_empty(self):
        self.assertEqual(list_crew([]), [])

    def test_list_crew_multiple(self):
        crew_list = [Crew("Charlie", "Doctor"), Crew("David", "Scientist")]
        expected_list = ["Charlie (Doctor)", "David (Scientist)"]
        self.assertEqual(list_crew(crew_list), expected_list)

    def test_create_crew_member_different_roles(self):
        crew_member1 = create_crew_member("Eve", "Captain")
        crew_member2 = create_crew_member("Frank", "Navigator")
        self.assertEqual(crew_member1.role, "Captain")
        self.assertEqual(crew_member2.role, "Navigator")

if __name__ == '__main__':
    unittest.main()