# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from settings.base import Base 

import sys
sys.path.append('/workspace/backend')

# @pytest.fixture(scope='function')
# def test_db_session():
#     engine = create_engine("sqlite:///:memory:")
#     Base.metadata.create_all(engine)
#     session = sessionmaker(bind=engine)()
#     yield session
#     session.close()
#     Base.metadata.drop_all(engine)
