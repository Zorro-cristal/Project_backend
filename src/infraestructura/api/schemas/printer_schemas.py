from typing import Literal, Optional

from pydantic import BaseModel, Field


class PrintAck(BaseModel):
    """Payload de confirmación (ACK) de impresión enviado por el cliente Flutter."""

    event: Literal["print_ack"] = "print_ack"
    job_id: str = Field(..., description="Id de la orden (job de impresión)")
    status: Literal["SUCCESS", "FAILED"] = Field(
        ..., description="Resultado de la impresión"
    )
    error_message: Optional[str] = Field(
        default=None, description="Mensaje de error si la impresión falló"
    )
