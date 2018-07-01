from copy import copy


def dpll(clauses):
    model = {}
    symbols = set()

    for clause in clauses:
        for literal in clause:
            symbols.add(literal[0])

    return dpll_with_model(clauses, symbols, model)


def evaluate_clause_with_model(clause, model):
    has_unassigned_variable = False
    for literal in clause:
        variable = literal[0]
        if variable not in model:
            has_unassigned_variable = True
            continue
        if literal[1] == model[variable]:
            return True
    if has_unassigned_variable:
        return None
    return False


def evaluate_clauses_with_model(clauses, model):
    undefined_clauses = []
    has_clause_with_undefined_result = False
    for clause in clauses:
        clause_result = evaluate_clause_with_model(clause, model)
        if clause_result is None:
            has_clause_with_undefined_result = True
            undefined_clauses.append(clause)
            continue
        if not clause_result:
            return False, undefined_clauses
    if has_clause_with_undefined_result:
        return None, undefined_clauses
    return True, undefined_clauses


def find_pure_symbols(clauses, symbols):
    symbols_instances = {}
    for clause in clauses:
        for literal in clause:
            if literal[0] in symbols_instances:
                symbols_instances[literal[0]].add(literal[1])
            else:
                symbols_instances[literal[0]] = {literal[1]}

    result = {}
    for symbol in symbols_instances.keys():
        if symbol in symbols and len(symbols_instances[symbol]) == 1:
            result[symbol] = symbols_instances[symbol].pop()

    if len(result) > 0:
        return result
    else:
        return None


def find_unit_clause(clauses):
    for clause in clauses:
        if len(clause) == 1:
            return clause
    return None


def dpll_with_model(clauses, symbols, model):
    model_result, undefined_clauses = evaluate_clauses_with_model(clauses, model)

    if model_result is not None:
        if model_result:
            return model
        else:
            return None

    pure_symbols = find_pure_symbols(undefined_clauses, symbols)

    new_model = copy(model)
    new_symbols = copy(symbols)

    if pure_symbols is not None:
        pure_symbol = next(iter(pure_symbols))
        new_model[pure_symbol] = pure_symbols[pure_symbol]
        new_symbols.remove(pure_symbol)
        return dpll_with_model(undefined_clauses, new_symbols, new_model)

    unit_clause = find_unit_clause(undefined_clauses)

    if unit_clause is not None:
        new_model[unit_clause[0][0]] = unit_clause[0][1]
        new_symbols.remove(unit_clause[0][0])
        return dpll_with_model(undefined_clauses, new_symbols, new_model)

    first_symbol = next(iter(symbols))
    new_symbols.remove(first_symbol)

    new_model[first_symbol] = True
    result_with_first_symbol_as_true = dpll_with_model(undefined_clauses, new_symbols, new_model)

    if result_with_first_symbol_as_true is not None:
        return result_with_first_symbol_as_true

    new_model[first_symbol] = False
    result_with_first_symbol_as_false = dpll_with_model(undefined_clauses, new_symbols, new_model)
    return result_with_first_symbol_as_false
