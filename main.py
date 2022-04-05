
from ariadne import QueryType, make_executable_schema, load_schema_from_path,format_error
from ariadne.asgi import GraphQL
from fastapi import FastAPI, HTTPException, Depends, Request
from .mutations import mutation
from .db.models import User,UserSequence
from ariadne import ScalarType
from .subscriptions import subscription
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
# from fastapi_jwt_auth import AuthJWT
# from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from .api import app
from .db.database import db
from graphql.error.graphql_error import GraphQLError
from .utils import security
from .utils.error import MyGraphQLError
from dateutil.parser import * 
type_defs = load_schema_from_path("schema.graphql")

# def my_format_error(error: GraphQLError, debug: bool = False) -> dict:
#     if debug:
#         return format_error(error, debug)

#     formatted = error.formatted
#     formatted["message"] = error.args[0]
#     return formatted

class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

# @AuthJWT.load_config
# def get_config():
#     return Settings()

# @app.exception_handler(AuthJWTException)
# def authjwt_exception_handler(request: Request, exc: AuthJWTException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.message}
#     )
query = QueryType()

@query.field("hello")
async def resolve_hello(_,info):
    #print(info.context)
    # for blog in info.context["request"]["headers"]:
    #     print(blog)
    user = await security.get_current_user_by_info(info)
    if not user:
        raise MyGraphQLError(code=401, message="User not authenticated")
    return "Hello world!"
@query.field("getSequences")
async def resolve_sequences(_,info):
    user = await security.get_current_user_by_info(info)
    if not user:
        raise MyGraphQLError(code=401, message="User not authenticated")

    print("user id : " + str(user.id))
    print("user name : " + str(user.name))
    return UserSequence.objects.filter(userId=user.id)


datetime_scalar = ScalarType("Datetime")

@datetime_scalar.serializer
def serialize_datetime(value):
    return value.isoformat()
@datetime_scalar.value_parser
def parse_datetime_value(value):
    # dateutil is provided by python-dateutil library
    return parser.parse(value)
schema = make_executable_schema(type_defs,query,mutation,subscription,datetime_scalar)
graphqlApp = GraphQL(schema, debug=True)
# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     return User.objects(id=identity['id'])[0]
#app.add_websocket_route("/graphql", graphqlApp)
#app.add_route("/graphql", graphqlApp)
app.mount("/graphql", graphqlApp)

#app.add_websocket_route("/graphql", graphqlApp)