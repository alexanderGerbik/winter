import pytest
from drf_yasg import openapi

import winter
from winter.pagination import PagePosition
from winter.pagination import PagePositionArgumentsInspector
from winter.pagination import PagePositionArgumentResolver
from winter.routing import get_route


@pytest.mark.parametrize(('argument_type', 'must_return_parameters'), (
    (PagePosition, True),
    (object, False),
))
def test_page_position_argument_inspector(argument_type, must_return_parameters):
    class SimpleController:
        @winter.route_get('')
        def method(self, arg1: argument_type):
            return arg1

    route = get_route(SimpleController.method)

    resolver = PagePositionArgumentResolver()
    inspector = PagePositionArgumentsInspector(resolver)

    if must_return_parameters:
        expected_parameters = [
            inspector.limit_parameter,
            inspector.offset_parameter,
            inspector.default_order_by_parameter,
        ]
    else:
        expected_parameters = []

    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert parameters == expected_parameters


def test_page_position_argument_inspector_with_allowed_order_by_fields():
    class SimpleController:
        @winter.route_get('')
        @winter.pagination.order_by(['id'])
        def method(self, arg1: PagePosition):
            return arg1

    route = get_route(SimpleController.method)

    resolver = PagePositionArgumentResolver()
    inspector = PagePositionArgumentsInspector(resolver)

    order_by_parameter = openapi.Parameter(
        name=resolver.order_by_name,
        description='Comma separated order by fields. Allowed fields: id',
        required=False,
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items={'type': openapi.TYPE_STRING},
    )

    expected_parameters = [
        inspector.limit_parameter,
        inspector.offset_parameter,
        order_by_parameter,
    ]

    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert parameters == expected_parameters
