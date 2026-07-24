

class AppError(Exception):
    """Base exception class"""


class OdooConnectionError(AppError):
    """retryable error for odoo conections"""


class OdooDataError(AppError):
    """odoo data is not valid"""


class RecordProcessingError(AppError):
    """Just a record processing error (mapping or saving) that should not stop the sync process"""

    def __init__(self, entity_type: str, odoo_id, original_exception: Exception):
        self.entity_type = entity_type
        self.odoo_id = odoo_id
        self.original_exception = original_exception
        super().__init__(
            f"error processing {entity_type} with odoo_id={odoo_id}: {original_exception}"
        )
