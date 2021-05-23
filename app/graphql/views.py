from . import graphql
from .schema import schema
from flask_graphql import GraphQLView

graphql.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
    )
)
