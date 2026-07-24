from app.database.base import Base
import app.models


for table_name in Base.metadata.tables:
    print(table_name)