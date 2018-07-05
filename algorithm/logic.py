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


def dpll(clauses, parallelism=0, model=None, result=None, stop_control=StopControl(), disable_unit_clause_heuristic=True):
    if model is None:
        model = {}

    index = symbol_index(clauses)

    for assigned_symbol in model.keys():
        del index[assigned_symbol]

    if parallelism == 0:
        return_value = dpll_with_model(clauses, index, model, stop_control, disable_unit_clause_heuristic)
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
    symbols = set()
    for literal in clause:
        variable = literal[0]
        symbols.add(variable)
        if variable not in model:
            has_unassigned_variable = True
            continue
        if literal[1] == model[variable]:
            return True, symbols
    if has_unassigned_variable:
        return None, symbols
    return False, symbols


def evaluate_clauses_with_model(clauses, model, index):
    new_index = copy(index)
    undefined_clauses = copy(clauses)
    for set_variable in model.keys():
        positive_literal_key = (set_variable, model[set_variable])
        if positive_literal_key in new_index:
            just_satisfied_clauses = new_index[positive_literal_key]
            for just_satisfied_clause in just_satisfied_clauses:
                if just_satisfied_clause in undefined_clauses:
                    undefined_clauses.remove(just_satisfied_clause)
                    if positive_literal_key in new_index:
                        del new_index[positive_literal_key]
                        for literal in just_satisfied_clause:
                            if literal in new_index:
                                if just_satisfied_clause in new_index[literal]:
                                    new_index[literal].remove(just_satisfied_clause)
                                    if len(new_index[literal]) == 0:
                                        del new_index[literal]

    for set_variable in model.keys():
        negative_literal_key = (set_variable, not model[set_variable])
        if negative_literal_key in new_index:
            probably_terminated_clauses = new_index[negative_literal_key]
            for probably_terminated_clause in probably_terminated_clauses:
                clause_is_not_unknown_yet = True
                for literal in probably_terminated_clause:
                    if literal[0] not in model:
                        clause_is_not_unknown_yet = False
                        break
                if clause_is_not_unknown_yet:
                    return False, undefined_clauses, new_index

    if len(undefined_clauses) == 0:
        return True, undefined_clauses, new_index

    return None, undefined_clauses, new_index
    # undefined_clauses = []
    # new_symbols = set()
    # has_clause_with_undefined_result = False
    # for clause in clauses:
    #     clause_result, clause_symbols = evaluate_clause_with_model(clause, model)
    #     if clause_result is None:
    #         has_clause_with_undefined_result = True
    #         undefined_clauses.append(clause)
    #         for clause_symbol in clause_symbols:
    #             new_symbols.add(clause_symbol)
    #         continue
    #     if not clause_result:
    #         return False, undefined_clauses, new_symbols.intersection(symbols)
    # if has_clause_with_undefined_result:
    #     return None, undefined_clauses, new_symbols.intersection(symbols)
    # return True, undefined_clauses, new_symbols.intersection(symbols)


def find_pure_symbols(index, model):
    result = {}
    for literal in index:
        if literal[0] not in model:
            if (literal[0], not literal[1]) not in index:
                result[literal[0]] = literal[1]
    if len(result.keys()) == 0:
        return None
    return result


def find_unit_clause(clauses):
    for clause in clauses:
        if len(clause) == 1:
            return clause
    return None


def dpll_with_model(clauses, index, model, stop_control, disable_unit_clause_heuristic):
    # be aware of signal to stop the search
    if stop_control.stop:
        return None
    model_result, undefined_clauses, new_index = evaluate_clauses_with_model(clauses, model, index)
    if model_result is not None:
        if model_result:
            return model
        else:
            return None

    new_model = copy(model)

    if stop_control.stop:
        return None

    pure_symbols = find_pure_symbols(new_index, new_model)

    if pure_symbols is not None:
        for pure_symbol in pure_symbols:
            new_model[pure_symbol] = pure_symbols[pure_symbol]

        if stop_control.stop:
            return None

        return dpll_with_model(undefined_clauses, new_index, new_model, stop_control, disable_unit_clause_heuristic)

    if not disable_unit_clause_heuristic:
        unit_clause = find_unit_clause(undefined_clauses)

        if unit_clause is not None:
            new_model[unit_clause[0][0]] = unit_clause[0][1]

            if stop_control.stop:
                return None

            return dpll_with_model(undefined_clauses, new_index, new_model, stop_control, disable_unit_clause_heuristic)

    first_symbol = None
    for literal in index.keys():
        if literal[0] not in model:
            first_symbol = literal[0]
            break

    if first_symbol is None:
        pass
    assert first_symbol is not None

    new_model[first_symbol] = True

    if stop_control.stop:
        return None

    result_with_first_symbol_as_true = dpll_with_model(undefined_clauses, new_index, new_model, stop_control,
                                                       disable_unit_clause_heuristic)
    if result_with_first_symbol_as_true is not None:
        return result_with_first_symbol_as_true

    if stop_control.stop:
        return None

    new_model[first_symbol] = False
    result_with_first_symbol_as_false = dpll_with_model(undefined_clauses, new_index, new_model, stop_control,
                                                        disable_unit_clause_heuristic)
    return result_with_first_symbol_as_false


def symbol_index(clauses):
    index = {}
    for clause in clauses:
        for literal in clause:
            if literal not in index:
                index[literal] = [clause]
            else:
                index[literal].append(clause)
    return index
