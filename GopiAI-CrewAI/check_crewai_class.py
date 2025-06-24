from crewai import Crew
import inspect

print('Crew class:', Crew)
print('Crew init signature:', inspect.signature(Crew.__init__))
print('Crew module:', Crew.__module__)
