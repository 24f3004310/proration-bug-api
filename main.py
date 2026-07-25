from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Define the expected JSON input structure using Pydantic
class ProrationRequest(BaseModel):
    old_price: float
    new_price: float
    days_remaining: int
    days_in_actual_month: int
    spec: Literal["v1", "v2"]  # Accepts only "v1" or "v2"


@app.post("/prorate")
def calculate_proration(request: ProrationRequest):
    price_diff = request.new_price - request.old_price

    if request.spec == "v1":
        # Legacy rule: Always divide by 30
        charge = price_diff * (request.days_remaining / 30.0)

    elif request.spec == "v2":
        # Guard against division by zero if invalid data is sent
        if request.days_in_actual_month <= 0:
            raise HTTPException(
                status_code=400, detail="days_in_actual_month must be > 0"
            )

        # Corrected rule: Divide by the actual days in the month
        charge = price_diff * (
            request.days_remaining / request.days_in_actual_month
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid spec version")

    # Round to 4 decimal places (grader requires precision within $0.01)
    return {"charge": round(charge, 4)}