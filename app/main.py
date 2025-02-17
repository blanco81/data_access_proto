from fastapi import FastAPI
from app.routes.folder import router as folder_router
from app.routes.assets import router as assets_router
from app.routes.language import router as language_router
from app.routes.tags import router as tags_router
from app.routes.feature import router as feature_router
from app.routes.feature_group import router as featureGroup_router
from app.routes.market import router as market_router
from app.routes.user import router as user_router


app = FastAPI()


@app.get("/")
def placeholder():
    return {"Hello": "World"}


app.include_router(folder_router, prefix="/folders", tags=["Folders"])
app.include_router(assets_router, prefix="/assets", tags=["Assets"])
app.include_router(language_router, prefix="/languages", tags=["Languages"])
app.include_router(tags_router, prefix="/tags", tags=["Tags"])
app.include_router(feature_router, prefix="/features", tags=["Features"])
app.include_router(
    featureGroup_router, prefix="/feature_groups", tags=["FeatureGroups"]
)
app.include_router(market_router, prefix="/markets", tags=["Markets"])
app.include_router(user_router, prefix="/users", tags=["Users"])
