
from fastapi import FastAPI, APIRouter, Body
from houston.service import execute_service
from typing import *
from datetime import datetime


def my_stage_executor(operation: str, message: Optional[str] = None):
    """
    Executes a Houston stage.

    :param operation: The operation to be run. This comes from the Houston stage params.
    :param message: Line added to the story when running the 'write-story' operation.
                    This isn't used by other operations, so it must be made optional.
    """
    now = datetime.now()

    if operation == "start-story":
        with open("story.txt", "w") as f:
            f.write(f"Once upon a time...\n")
    elif operation == "write-story":
        with open("story.txt", "a") as f:
            f.write(f"At {now.strftime('%H:%M:%S.%f')}, {message}.\n")
    elif operation == "end-story":
        with open("story.txt", "a") as f:
            f.write("THE END\n")

    else:
        raise ValueError(f"Unknown operation '{operation}'.")


#
# HTTP server setup
#


app = FastAPI(title=f"Local HTTP Service")

router = APIRouter()


@router.post("/houston")
def post_houston(
        event: Dict = Body()
):
    """
    Execute a Houston stage
    """
    execute_service(
        event=event,
        func=my_stage_executor
    )

    return "Success!"


app.include_router(router)
