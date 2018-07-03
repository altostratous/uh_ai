import queue
from copy import copy

from threading import Thread, Lock


class StopControl(object):
    def __init__(self) -> None:
        super().__init__()
        self.stop = False
        self.lock = Lock()

    def signal_stop(self):
        self.lock.acquire()
        self.stop = True
        self.lock.release()


def dpll(clauses, parallelism=0, model=None, result=None, stop_control=StopControl()):
    if model is None:
        model = {}

    symbols = set()
    for clause in clauses:
        for literal in clause:
            symbols.add(literal[0])

    for assigned_symbol in model.keys():
        symbols.remove(assigned_symbol)

    if parallelism == 0:
        return_value = dpll_with_model(clauses, symbols, model, stop_control)
        if result is not None:
            result.put(return_value)
        return return_value

    # fork the context
    first_model = copy(model)
    second_model = copy(model)
    inner_result = queue.Queue()

    # divide the problem into subsets and run them asynchronously
    symbol_to_assign = symbols.pop()
    first_model[symbol_to_assign] = True
    second_model[symbol_to_assign] = False
    first_thread = Thread(target=dpll, args=(clauses, parallelism - 1, first_model, inner_result, stop_control))
    second_thread = Thread(target=dpll, args=(clauses, parallelism - 1, second_model, inner_result, stop_control))
    first_thread.start()
    second_thread.start()

    # wait to finish
    results_count = 0
    return_value = None
    while results_count < 2 and return_value is None:
        return_value = inner_result.get()
        results_count += 1

    # if the answer is found stop all threads in this search
    if return_value is not None:
        stop_control.signal_stop()

    # gracefully join the child threads
    if first_thread.is_alive():
        first_thread.join()
    if second_thread.is_alive():
        second_thread.join()

    if result is not None:
        result.put(return_value)
    return return_value


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
    symbols_set = set(symbols)
    for clause in clauses:
        for literal in clause:
            if literal[0] not in symbols_set:
                continue
            if literal[0] in symbols_instances:
                symbols_instances[literal[0]].add(literal[1])
            else:
                symbols_instances[literal[0]] = {literal[1]}

    result = {}
    for symbol in symbols_instances.keys():
        if len(symbols_instances[symbol]) == 1:
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


def dpll_with_model(clauses, symbols, model, stop_control):
    # be aware of signal to stop the search
    if stop_control.stop:
        return None
    model_result, undefined_clauses = evaluate_clauses_with_model(clauses, model)
    if model_result is not None:
        if model_result:
            return model
        else:
            return None

    new_model = copy(model)

    new_symbols = set()
    for clause in undefined_clauses:
        for literal in clause:
            new_symbols.add(literal[0])
    new_symbols = new_symbols.intersection(symbols)

    if stop_control.stop:
        return None

    pure_symbols = find_pure_symbols(undefined_clauses, new_symbols)

    if pure_symbols is not None:
        for pure_symbol in pure_symbols:
            new_model[pure_symbol] = pure_symbols[pure_symbol]
            new_symbols.remove(pure_symbol)

        if stop_control.stop:
            return None

        return dpll_with_model(undefined_clauses, new_symbols, new_model, stop_control)

    unit_clause = find_unit_clause(undefined_clauses)

    if unit_clause is not None:
        new_model[unit_clause[0][0]] = unit_clause[0][1]
        new_symbols.remove(unit_clause[0][0])

        if stop_control.stop:
            return None

        return dpll_with_model(undefined_clauses, new_symbols, new_model, stop_control)

    first_symbol = next(iter(symbols))
    new_symbols.remove(first_symbol)
    new_model[first_symbol] = True

    if stop_control.stop:
        return None

    result_with_first_symbol_as_true = dpll_with_model(undefined_clauses, new_symbols, new_model, stop_control)
    if result_with_first_symbol_as_true is not None:
        return result_with_first_symbol_as_true

    if stop_control.stop:
        return None

    new_model[first_symbol] = False
    result_with_first_symbol_as_false = dpll_with_model(undefined_clauses, new_symbols, new_model, stop_control)
    return result_with_first_symbol_as_false
