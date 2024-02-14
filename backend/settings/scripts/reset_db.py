from ... import database
from ...entities.base import Base

# Reset Tables
Base.metadata.drop_all(database.engine)
Base.metadata.create_all(database.engine)
