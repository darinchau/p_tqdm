"""Map functions with tqdm progress bars for parallel and sequential processing.

p_map: Performs a parallel ordered map.
p_imap: Returns an iterator for a parallel ordered map.
p_umap: Performs a parallel unordered map.
p_uimap: Returns an iterator for a parallel unordered map.
t_map: Performs a sequential map.
t_imap: Returns an iterator for a sequential map.
"""

from collections.abc import Sized
from typing import Any, Callable, Generator, Iterable, List

from pathos.helpers import cpu_count
from pathos.multiprocessing import ProcessPool
from pathos.threading import ThreadPool
from tqdm import tqdm

def _parallel(ordered: bool, function: Callable, mode: str, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a parallel map with a progress bar.

    Arguments:
        ordered(bool): True for an ordered map, false for an unordered map.
        function(Callable): The function to apply to each element of the given Iterables.
        mode(str): "threaded" or "parallel"
        iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.

    Returns:
        A generator which will apply the function to each element of the given Iterables
        in parallel in order with a progress bar.
    """

    # Extract num_cpus
    num_cpus = kwargs.pop('num_cpus', None)

    # Determine num_cpus
    if num_cpus is None:
        num_cpus = cpu_count()
    elif type(num_cpus) == float:
        num_cpus = int(round(num_cpus * cpu_count()))

    # Determine length of tqdm (equal to length of shortest iterable or total kwarg), if possible
    total = kwargs.pop('total', None)
    lengths = [len(iterable) for iterable in iterables if isinstance(iterable, Sized)]
    length = total or (min(lengths) if lengths else None)

    # Create parallel generator
    map_type = 'imap' if ordered else 'uimap'
    assert mode and mode in ("parallel", "threading"), f"Internal error: recieved unknown mode {mode}"
    pool = ProcessPool(num_cpus) if mode == "parallel" else ThreadPool(num_cpus)
    map_func = getattr(pool, map_type)

    # Choose tqdm variant
    tqdm_func = kwargs.pop('tqdm', tqdm)

    for item in tqdm_func(map_func(function, *iterables), total=length, **kwargs):
        yield item

    pool.clear()

def p_imap(function: Callable, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a parallel ordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = _parallel(True, function, "parallel", *iterables, **kwargs)

    return generator

def p_map(function: Callable, *iterables: Iterable, **kwargs: Any) -> List[Any]:
    """Performs a parallel ordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = p_imap(function, *iterables, **kwargs)
    result = list(generator)

    return result

def p_uimap(function: Callable, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a parallel unordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = _parallel(False, function, "parallel", *iterables, **kwargs)

    return generator


def p_umap(function: Callable, *iterables: Iterable, **kwargs: Any) -> List[Any]:
    """Performs a parallel unordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = p_uimap(function, *iterables, **kwargs)
    result = list(generator)

    return result


def _sequential(function: Callable, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a sequential map with a progress bar.

    Arguments:
        function(Callable): The function to apply to each element of the given Iterables.
        iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.

    Returns:
        A generator which will apply the function to each element of the given Iterables
        sequentially in order with a progress bar.
    """

    # Determine length of tqdm (equal to length of shortest iterable)
    length = min(len(iterable) for iterable in iterables if isinstance(iterable, Sized))

    # Create sequential generator
    for item in tqdm(map(function, *iterables), total=length, **kwargs):
        yield item

def s_imap(function: Callable, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a sequential map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use"""

    generator = _sequential(function, *iterables, **kwargs)

    return generator

def s_map(function: Callable, *iterables: Iterable, **kwargs: Any) -> List[Any]:
    """Performs a sequential map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - kwargs already present in tqdm"""

    generator = s_imap(function, *iterables, **kwargs)
    result = list(generator)

    return result

def t_imap(function: Callable, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a multithreaded ordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = _parallel(True, function, "threading", *iterables, **kwargs)

    return generator

def t_map(function: Callable, *iterables: Iterable, **kwargs: Any) -> List[Any]:
    """Performs a multithreaded ordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = p_imap(function, *iterables, **kwargs)
    result = list(generator)

    return result

def t_uimap(function: Callable, *iterables: Iterable, **kwargs: Any) -> Generator:
    """Returns a generator for a multithreaded unordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = _parallel(False, function, "threading", *iterables, **kwargs)

    return generator


def t_umap(function: Callable, *iterables: Iterable, **kwargs: Any) -> List[Any]:
    """Performs a multithreaded unordered map with a progress bar.
    
    Arguments:
        - function(Callable): The function to apply to each element of the given Iterables.
        - iterables(Tuple[Iterable]): One or more Iterables containing the data to be mapped.
    
    Keyword arguments:
        - num_cpus(int): Number of cpus to use. If unspecified, use all cpus
        - total(int): total elements in the iterator. If unspecified, this number will be automatically determined using the iterators
        - tqdm(tqdm object): the tqdm progress bar to use
        - other kwargs already present in tqdm"""

    generator = p_uimap(function, *iterables, **kwargs)
    result = list(generator)

    return result