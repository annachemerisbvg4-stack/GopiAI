"""
GopiAI Core Package

Base interfaces, exceptions, and schema definitions for the GopiAI system.
"""

__version__ = "2.0.0"
__author__ = "GopiAI Team"

from .core import interfaces, exceptions, schema

__all__ = ["interfaces", "exceptions", "schema"]