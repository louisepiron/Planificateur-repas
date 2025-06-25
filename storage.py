import json
import os

RECIPES_FILE = "recettes.json"
USERS_FILE = "users.json"
MENUS_FILE = "menus.json"

def charger_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def sauvegarder_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def charger_recettes():
    return charger_json(RECIPES_FILE, [])

def sauvegarder_recettes(recettes):
    sauvegarder_json(recettes, RECIPES_FILE)

def charger_users():
    return charger_json(USERS_FILE, {})

def sauvegarder_users(users):
    sauvegarder_json(users, USERS_FILE)

def charger_menus():
    return charger_json(MENUS_FILE, {})

def sauvegarder_menus(menus):
    sauvegarder_json(menus, MENUS_FILE)