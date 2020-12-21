"""Tools to view and search for rules."""
import json
import re
import typing

import discord
from discord.ext import commands

from . import menus


def load_data() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Load the rules from JSON and index the categories."""
    with open('rules.json') as f:
        data = json.load(f)
    rules = data['rules']
    categories = data['categories']
    searchable_categories = {
        make_string_searchable(name): number
        for number, name in categories.items()
    }
    return rules, categories, searchable_categories


def make_string_searchable(original: str) -> str:
    """Remove special characters from a string and make it lowercase."""
    return re.sub('[^a-z]', '', original.lower())


def rule_exists(rule_id: str) -> bool:
    """Check if a rule exists."""
    return rule_id in RULES


def get_category(search: str) -> typing.Optional[str]:
    """Search for a category ID by name.

    If a valid category ID is passed, returns it.
    """
    if search in CATEGORIES:
        return search
    search = make_string_searchable(search)
    return SEARCHABLE_CATEGORIES.get(search)


def get_rule(rule_id: str) -> typing.Optional[str]:
    """Get a specific rule by its number, eg. `5.2`."""
    return RULES.get(rule_id, 'Could not find that rule.')


def get_category_index(category_number: str) -> dict[str, str]:
    """Get a preview of all rules in a category."""
    rules = {}
    for rule_id, rule in RULES.items():
        if rule_id.startswith(category_number):
            rules[rule_id] = '**{rule_id}** - {rule:.40}...'.format(
                rule_id=rule_id, rule=rule.replace('\n', ' ')
            )
    return rules


def get_all_categories_index() -> dict[str, str]:
    """Get the index of all categories."""
    return {
        category_number: f'{category_number} - {category_name}'
        for category_number, category_name in CATEGORIES.items()
    }


RULES, CATEGORIES, SEARCHABLE_CATEGORIES = load_data()
