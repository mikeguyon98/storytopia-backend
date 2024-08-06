Using HTTPException from FastAPI directly in your service or repository layers isn't the best practice as it tightly couples these layers with FastAPI, which can make your code less reusable and harder to test. Instead, it's better to use custom exceptions in the lower layers and convert them to HTTPException in the controller layer.

Here's an updated example that includes converting custom exceptions to HTTPException in the controller layer:

Step 1: Define Custom Exceptions
```python
# exceptions.py
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

class DatabaseError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
```

Step 2: Repository Layer
```python
# repository.py
from .exceptions import ItemNotFoundError, DatabaseError

def find_item_in_database(item_id: int):
    # Simulated database lookup
    if item_id == 0:  # Simulate not found
        return None
    elif item_id < 0:  # Simulate database error
        raise Exception("Simulated database connection error")
    return {"id": item_id, "name": "Sample Item"}

def get_item_from_db(item_id: int):
    try:
        item = find_item_in_database(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item
    except Exception as e:
        raise DatabaseError(detail=str(e))
```
Step 3: Service Layer
```python
# service.py
from .repository import get_item_from_db
from .exceptions import ItemNotFoundError, DatabaseError

def get_item_service(item_id: int):
    try:
        return get_item_from_db(item_id)
    except ItemNotFoundError as e:
        raise e
    except DatabaseError as e:
        raise e
```
Step 4: Controller Layer
```python
# controller.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .service import get_item_service
from .exceptions import ItemNotFoundError, DatabaseError

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    try:
        item = get_item_service(item_id)
        return item
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Item with ID {e.item_id} not found")
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e.detail}")

@app.exception_handler(ItemNotFoundError)
async def item_not_found_exception_handler(request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item with ID {exc.item_id} not found"},
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request, exc: DatabaseError):
    return JSONResponse(
        status_code=500,
        content={"message": f"Database error: {exc.detail}"},
    )
```
Summary
Define custom exceptions in exceptions.py.
Raise custom exceptions in the repository.py when encountering errors.
Propagate these exceptions through the service.py without converting them.
Catch and convert these exceptions to HTTPException in the controller.py.
This approach keeps the business logic and database interactions separate from the HTTP handling logic, making your application more modular and easier to maintain.
