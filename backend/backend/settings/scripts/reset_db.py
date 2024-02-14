from ... import database
from ..base import Base

# Reset Tables
Base.metadata.drop_all(database.engine)
Base.metadata.create_all(database.engine)