class IngestionError(Exception):
    pass


class ConfigError(IngestionError):
    pass


class VendorError(IngestionError):
    pass


class ValidationError(IngestionError):
    pass


class WriterError(IngestionError):
    pass


class CheckpointError(IngestionError):
    pass
