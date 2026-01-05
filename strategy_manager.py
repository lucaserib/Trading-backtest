import json
import os
from datetime import datetime

STRATEGIES_FILE = "saved_strategies.json"

def load_strategies():
    """Carrega todas as estratégias salvas do arquivo JSON"""
    if not os.path.exists(STRATEGIES_FILE):
        return {}

    try:
        with open(STRATEGIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_strategy(name, code, params=None):
    """
    Salva uma estratégia no arquivo JSON
    params pode incluir: fast_length, slow_length, etc
    """
    strategies = load_strategies()

    strategies[name] = {
        'name': name,
        'code': code,
        'params': params or {},
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    with open(STRATEGIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(strategies, f, indent=2, ensure_ascii=False)

    return True

def delete_strategy(name):
    """Remove uma estratégia do arquivo"""
    strategies = load_strategies()

    if name in strategies:
        del strategies[name]
        with open(STRATEGIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, indent=2, ensure_ascii=False)
        return True
    return False

def get_strategy(name):
    """Retorna uma estratégia específica"""
    strategies = load_strategies()
    return strategies.get(name)

def list_strategy_names():
    """Retorna lista de nomes de todas as estratégias"""
    strategies = load_strategies()
    return list(strategies.keys())
