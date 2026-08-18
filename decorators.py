from time import sleep, time
from functools import wraps
import tracemalloc
import os
import json
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env.config")

def save_result(filename):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(filename, "a", encoding="utf-8") as f:
                f.write(
                    f"{func.__name__}"
                    f"(args={args}, kwargs={kwargs})"
                    f" -> {result}\n"
                )
            return result
        return wrapper
    return decorator


def count_calls(func):
    count = 0
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        print(f"{func.__name__} called {count} times")
        return func(*args, **kwargs)
    return wrapper


def retry(times=os.environ.get("RETRY"), delay=1, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    print(
                        f"Attempt {attempt}/{times} failed: {e}"
                    )
                    if attempt < times:
                        sleep(delay)
            raise last_error
        return wrapper
    return decorator


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get("DEBUG") != "1":
            return func(*args, **kwargs)
        inicio = time()
        resultado = func(*args, **kwargs)
        fim = time()
        print(f"Tempo {func.__name__}: {fim - inicio:.4f}s")
        return resultado
    return wrapper


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get("DEBUG") != "1":
            return func(*args, **kwargs)
        print(f"Iniciando {func.__name__}")
        resultado = func(*args, **kwargs)
        print(f"Finalizando {func.__name__}")
        return resultado
    return wrapper


def cache(func):
    memory = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get("CACHE") != "1":
            return func(*args, **kwargs)
        key = args + tuple(sorted(kwargs.items()))
        if key not in memory:
            memory[key] = func(*args, **kwargs)
        return memory[key]
    return wrapper


def memory_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if os.environ.get("MEMORY_USAGE") != "1":
            return func(*args, **kwargs)
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        print(f"Peak: {peak / 1024:.2f} KB")
        tracemalloc.stop()
        return result
    return wrapper


def save_json(filename):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(filename, "a", encoding="utf-8") as f:
                json.dump(result, f)
                f.write("\n")
            return result
        return wrapper
    return decorator