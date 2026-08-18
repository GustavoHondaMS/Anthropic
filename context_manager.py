from contextlib import contextmanager

@contextmanager
def SafeContext():
    print("start safe container")

    try:
        yield
    except Exception as e:
        print(f"Erro: {e}")

class SafeContainer:
    def __enter__(self):
        print("start safe container")

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f"Erro Value: {exc_value}")
            print(f"Erro Type: {exc_type}")
            print(f"Erro traceback: {traceback}")
            print(f"continuando a execução do programa...")
            return True 
        else:
            print("end")